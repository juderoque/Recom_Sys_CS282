# data setting
#domain = 'AMAZON_FASHION'
#domain = 'Gift_Cards'
#domain = 'Video_Games'
domain = 'All_Beauty'
#domain = 'Movies_and_TV'

# model setting
embedding_type = 'glove'
rnn_type = 'GRU'
dssm_type = 'simple_fc'
ds_type = 'cff'
# actual batch_size is batch_size * accumulation_steps
# that's an optimization for poor group like us QAQ
batch_size = 64
accumulation_steps = 1
pro_n_sen = 50
rev_n_sen = 20
seq_len = 150
fm_embed_dim = 100
n_head = 12
n_attn = 2
d_k = d_v = 64
n_rnn = 1
rnn_hidden_dim = 50

# training setting
to_gpu = True
test_ratio = 0.1
valid_ratio = 0.1
no_of_iter = 500
lr = 1e-4
weight_decay = 1e-6
cuda_index = 0
pretrain_freeze = True
dropout = 0.5

#start_from = '../model/checkpoint.model'
start_from = None
early_stop_steps = 20

# test setting
valid_size = 64