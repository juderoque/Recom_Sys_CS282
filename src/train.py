import torch
import torch.nn as nn
import torch.optim as optim

import numpy as np

import logging
import sys
import matplotlib.pyplot as plt

from Products import Products, prepare_prod_batch
from Reviews import Reviews, prepare_rev_batch
from embeddings import get_embed_layer
from model import RecomModel
from conf import *

# initialize logger
def init_weights(m):
    if type(m) == nn.Linear:
        torch.nn.init.xavier_uniform(m.weight)
        
def parse_logger(string=''):
    if not string:
        ret = logging.getLogger('stdout')
        hdlr = logging.StreamHandler(sys.stdout)
    else:
        ret = logging.getLogger(string)
        hdlr = logging.FileHandler(string)
    ret.setLevel(logging.INFO)
    ret.addHandler(hdlr)
    hdlr.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
    return ret
   
def prepare_batch_data(idx_batch):

    rev_idx_batch = [p[0] for p in idx_batch]
    prod_idx_batch = [p[1] for p in idx_batch]

    rev_batch = [r.get_reviews(rev_idx=rev_idx) for rev_idx in rev_idx_batch]
    # rev_batch = [r.get_reviews(rev_idx, prod_idx) 
    #            for rev_idx, prod_idx in zip(rev_idx_batch, prod_idx_batch)]
    # prod_batch = [p.get_product(idx, reduce=True) for idx in prod_idx_batch]
    prod_batch = [r.get_reviews(pro_idx=prod_idx) for prod_idx in prod_idx_batch]
    score_batch = [r.get_rating(rev_idx, pro_idx, True)[0] \
                   for rev_idx, pro_idx in zip(rev_idx_batch, prod_idx_batch)]

    target = torch.tensor(score_batch).float()

    #text, bop = prepare_prod_batch(prod_batch, tokenizer, seq_len)
    prod = prepare_rev_batch(prod_batch, tokenizer, pro_n_sen, seq_len)
    rev = prepare_rev_batch(rev_batch, tokenizer, rev_n_sen, seq_len)
    
    if to_gpu:
        target = target.cuda()
        #text = text.cuda()
        #bop = bop.cuda()
        rev = [r.cuda() for r in rev]
        prod = [r.cuda() for r in prod]
    
    #return text, bop, rev, target
    return rev, prod, target

logger = parse_logger()
logger.setLevel(logging.INFO)

# get data
logger.info("start loading data")
p = Products(domain)
r = Reviews(domain)
# how to split train and test data
# and how to fetch data by batch
r.train_test_split(test_ratio, valid_ratio)
print(f"Size train: {len(r.idx_train)} valid: {len(r.idx_valid)} test: {len(r.idx_test)}")
logger.info("ended loading data")

# get tokenizer and embedding setting
tokenizer, embedding, embed_dim = get_embed_layer(embedding_type)

model = RecomModel(rnn_hidden_dim, rnn_hidden_dim,
                   n_head, seq_len, 
                   pro_n_sen, rev_n_sen,
                   d_k, d_v,
                   embedding,
                   embed_dim,
                   n_rnn,
                   fm_field_dims=[2] * fm_n,
                   fm_embed_dim=fm_embed_dim,
                   rnn_type=rnn_type,
                   fm_type=fm_type,
                   dropout=0.1,)
                   
model.apply(init_weights)

if to_gpu:
    to_index = cuda_index
    model = nn.DataParallel(model, device_ids=[cuda_index])
    device = torch.device(f"cuda:{to_index}")
    logger.info(f'sending whole model data to CUDA device {str(device)}')
    model.to(device)


logger.info(f"Model is on gpu: {next(model.parameters()).is_cuda}")

criterion = nn.MSELoss()
#criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=lr, weight_decay=weight_decay)

loss_track, acc_track = [], []

logger.info('start training')
for no in range(no_of_iter):
    model.zero_grad()
    
    train_idx_batch = r.get_batch_bikey(batch_size, src='train')
    rev, prod, target = prepare_batch_data(train_idx_batch)

    #res = model(text, bop, rev)
    res = model(prod, rev)
    loss = criterion(res, target)
    
    loss.backward()
    optimizer.step()
    
    loss_track.append(loss)
    if no % 10 == 0:
        with torch.no_grad():
            valid_idx_batch = r.get_batch_bikey(valid_size, src='valid')
            rev, prod, target = prepare_batch_data(valid_idx_batch)
            res = model(prod, rev)
            valid_loss = criterion(res, target)
            logger.info(
                f'{no}/{no_of_iter} of iterations, current train loss: {loss:.4}, valid loss: {valid_loss:.4}'
            )
            #if valid_loss < 1.3:
            #    break
    

x = list(range(len(loss_track)))

plt.plot(x, loss_track)
plt.savefig('training_record.jpg')

# start testing
test_size = len(r.idx_test)
test_loss_list = []
num = 0
with torch.no_grad():
    test_idx = r.get_batch_bikey(test_size, src='test')
    for fold_no in range(test_size // batch_size + 1):
        test_idx_batch = test_idx[fold_no * batch_size:fold_no * batch_size + batch_size]
        if not len(test_idx_batch):
            continue
        num += 1
        rev, prod, target = prepare_batch_data(test_idx_batch)
        res = model(prod, rev)
        fold_loss = criterion(res, target)
        loss += fold_loss
        if fold_no == 0:
            print("fold_0:", res, target)
        if fold_no % 10 == 0:
            print(fold_loss)
test_loss = loss / num
logger.info(f'testing loss: {test_loss:.4}')