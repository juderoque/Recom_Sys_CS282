# data setting
domain = 'Gift_Cards'

# model setting
embedding_type = 'bert'
rnn_type = 'GRU'
fm_type = 'fm'
batch_size = 16
n_reviews = 5
seq_len = 100
fm_n = 2000
fm_embed_dim = 16
n_head = 16
d_k = d_v = 64
n_rnn = 2
rnn_hidden_dim = 400

# training setting
to_gpu=True
test_ratio = 0.2
no_of_iter = 120
lr=1e-5
weight_decay=1e-4
cuda_index=0
pretrain_freeze=True

# test setting
test_size = 20

