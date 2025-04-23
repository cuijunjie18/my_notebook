# ICT-COMP NOTES

# 有待探索的优化思路

- TP
- 显存优化选项
- OMP_NUM_THREAD
- Decord num_threads
- 视频预处理时间？
- 气泡填充？
- optimization-level
- 使用ramfs加速模型加载？
- fused AdamW

# 优化思路

- TP，模型分割，Padding、合并，框架支持，不同并行配置比较
- IO，ramfs，mmap，numworker
- 数据集B适配，格式处理
- 加速参数，融合算子，overlap，COC，优化器
- dataloader prefetch
- profiling
- 数据集排序

# 环境配置

<aside>
💡

注意：所有数据放在/home/ma-user/work下，否则重启会清空！

</aside>

## MindSpeed-MM

**相关资料**

- https://gitee.com/ascend/MindSpeed-MM
- https://www.hiascend.com/document/detail/zh/ModelZoo/pytorchframework/ptes/ptes_00028.html
- uv torch-npu版本选择 https://www.hiascend.com/document/detail/zh/Pytorch/600/configandinstg/instg/insg_0001.html

**安装步骤**

```bash
# in /path/to/workspace
export GIT_SSL_NO_VERIFY=true # 服务器证书问题
git clone https://gitee.com/ascend/MindSpeed-MM.git

cd MindSpeed-MM
uv python pin 3.10
uv sync
uv add decorator
uv add pyyaml wheel setuptools
1
# torch-npu由于证书问题无法通过URL安装
# uv add https://gitee.com/ascend/pytorch/releases/download/v6.0.rc3-pytorch2.1.0/torch_npu-2.1.0.post8-cp310-cp310-manylinux_2_17_aarch64.manylinux2014_aarch64.whl
wget https://gitee.com/ascend/pytorch/releases/download/v6.0.rc3-pytorch2.1.0/torch_npu-2.1.0.post8-cp310-cp310-manylinux_2_17_aarch64.manylinux2014_aarch64.whl
uv add ./torch_npu-2.1.0.post8-cp310-cp310-manylinux_2_17_aarch64.manylinux2014_aarch64.whl

# 验证安装
uv run python -c "import torch;import torch_npu;print(torch_npu.npu.is_available())"
uv run python -c "import torch;import torch_npu; a = torch.randn(3, 4).npu(); print(a + a);"
```

```bash
# in ./MindSpeed-MM
git clone https://github.com/NVIDIA/Megatron-LM.git

cd Megatron-LM
git checkout core_r0.8.0
cp -r megatron ../

cd ..
mkdir logs dataset ckpt
```

## APEX

- https://gitee.com/ascend/apex

```bash
# in ./MindSpeed-MM
git clone -b master https://gitee.com/ascend/apex.git

cd apex/
uv add "setuptools<=65.7.0"
vim scripts/build.sh # 修改脚本兼容uv
# 将117行 python"${PY_VERSION}" setup.py --cpp_ext bdist_wheel
# 改为    uv run python setup.py --cpp_ext bdist_wheel
bash scripts/build.sh --python=3.10

uv add ./apex/dist/apex-0.1+ascend-cp310-cp310-linux_aarch64.whl
```

## MindSpeed

- Mind-Speed-MM - InternVL2.5 使用指南https://gitee.com/ascend/MindSpeed-MM/tree/master/examples/internvl2.5
- https://gitee.com/ascend/MindSpeed

```bash
# in ./MindSpeed-MM
git clone https://gitee.com/ascend/MindSpeed.git

cd MindSpeed
# checkout commit from MindSpeed core_r0.8.0
git checkout 3f09d6736571cf1e30f8ac97de77982d0ab32cc5
uv add -r requirements.txt
```

修改脚本 `setup.py` 以兼容uv：

`./MindSpeed-MM/MindSpeed/setup.py:47-48` （注释掉，前面已经安装过requirements.txt）

```python
# if os.getenv('CI_BUILD', '0') != '1':
#     subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
```

```bash
# in MindSpeed-MM
uv add --editable ./MindSpeed

cp examples/internvl2.5/dot_product_attention.py MindSpeed/mindspeed/core/transformer/dot_product_attention.py
```

## 安装decord

```bash
# in ~
git clone --recursive https://github.com/dmlc/decord
cd decord
mkdir build && cd build
cmake .. -DUSE_CUDA=0 -DCMAKE_BUILD_TYPE=Release
make -j64
```

然后在Mindspeed-mm中运行 

```bash
uv add 绝对路径to decord/python
```

## 模型权重

在 `/home/ma-user/work/models` 

- OpenGVLab/InternVL2_5-78B：已下载
- OpenGVLab/InternVL2_5-2B：已下载
- OpenGVLab/InternVL2_5-8B：已下载

# 权重转换

`examples/intervl2.5/`

```bash
uv run python internvl2.5_convert_to_mm_ckpt.py --model-size 8B --load-dir /home/ma-user/work/models/InternVL2_5-8B --save-dir /home/ma-user/work/models_ms/InternVL2_5-2B --trust-remote-code True
```

# 推理迁移

## intervl2.5-2B

1. 权重转换：参考./MindSpeed-MM/examples/internvl2.5/[README.md](http://readme.md/)中的指导，使用python脚本将权重从safetensors格式转换成pt格式
2. 修改./MindSpeed-MM/examples/internvl2.5/inference_internvl.sh文件如下：
    
    ```bash
    #!/bin/bash
    source /usr/local/Ascend/ascend-toolkit/set_env.sh
    export ASCEND_SLOG_PRINT_TO_STDOUT=0
    export ASCEND_GLOBAL_LOG_LEVEL=3
    export TASK_QUEUE_ENABLE=2
    export COMBINED_ENABLE=1
    export CPU_AFFINITY_CONF=1
    export HCCL_CONNECT_TIMEOUT=1200
    export CUDA_DEVICE_MAX_CONNECTIONS=1
    export ACLNN_CACHE_LIMIT=100000
    
    # 经过测试暂不支持多卡并行
    NPUS_PER_NODE=1
    MASTER_ADDR=localhost
    MASTER_PORT=6000
    NNODES=1
    NODE_RANK=0
    WORLD_SIZE=$(($NPUS_PER_NODE*$NNODES))
    
    MBS=1
    GRAD_ACC_STEP=1
    TP=1
    PP=1
    CP=1
    DP=$(($WORLD_SIZE/$TP/$PP/$CP))
    GBS=$(($MBS*$GRAD_ACC_STEP*$DP))
    
    # 模型结构、推理配置描述文件
    MM_MODEL="/home/ma-user/work/qzy/MindSpeed-MM/examples/internvl2.5/inference_2B.json"
    
    MM_ARGS="
        --mm-model ${MM_MODEL} \
    "
    
    DISTRIBUTED_ARGS="
        --nproc_per_node $NPUS_PER_NODE \
        --nnodes $NNODES \
        --node_rank $NODE_RANK \
        --master_addr $MASTER_ADDR \
        --master_port $MASTER_PORT
    "
    
    GPT_ARGS="
        --tensor-model-parallel-size ${TP} \
        --pipeline-model-parallel-size ${PP} \
        --context-parallel-size ${CP} \
        --micro-batch-size ${MBS} \
        --global-batch-size ${GBS} \
        --seq-length 4096 \
        --tokenizer-type NullTokenizer \
        --vocab-size 151674 \
        --position-embedding-type rope \
        --rotary-base 1000000 \
        --swiglu \
        --no-masked-softmax-fusion \
        --use-distributed-optimizer \
        --bf16 \
        --trust-remote-code \
    "
    
    OUTPUT_ARGS="
        --log-interval 1 \
        --save-interval 5000 \
        --eval-interval 5000 \
        --eval-iters 5000 \
    "
    
    logfile=$(date +%Y%m%d)_$(date +%H%M%S)
    mkdir -p logs
    
    # 激活uv环境
    source /home/ma-user/work/qzy/MindSpeed-MM/.venv/bin/activate
    torchrun $DISTRIBUTED_ARGS \
        /home/ma-user/work/qzy/MindSpeed-MM/inference_vlm.py \
        $GPT_ARGS \
        $MM_ARGS \
        $OUTPUT_ARGS \
        --distributed-backend nccl \
        | tee logs/inference_${logfile}.log 2>&1
    
    set +x
    ```
    
3. 新增inference_2B.json，主要的迁移工作集中在该文件的配置上，要根据不同大小（2B/4B/78B/…）模型的vision_model和language_model类型、layers层数等参数对该文件进行改写。
    
    ```bash
    {
        "infer_data_type": "image",
        "file_path": "/home/ma-user/work/qzy/MindSpeed-MM/examples/internvl2.5/view.jpg",
        "prompts": "Please describe the image shortly.",
        "pipeline_class": "InternVLPipeline",
        "from_pretrained": "/home/ma-user/work/models_ms/InternVL2_5-2B/release/mp_rank_00/model_optim_rng.pt",
        "template": "internvl2_5",
        "dtype": "bf16",
        "device": "npu",
        "pre_process": true,
        "post_process": true,
        "add_text_encoder": false,
        "img_embedding_idx": 1,
        "downsample_ratio": 0.5,
        "select_layer": -1,
        "ps_version": "v2",
        "img_context_token_id": 92546,
        "num_segments": 8,
        "text_decoder": {
            "model_id": "internllm",
            "num_layers": 24,
            "hidden_size": 2048,
            "num_attention_heads": 16,
            "num_query_groups": 8,
            "ffn_hidden_size": 8192,
            "kv_channels": 128,
            "hidden_dropout": 0.0,
            "attention_dropout": 0.0,
            "layernorm_epsilon": 1e-06,
            "normalization": "RMSNorm",
            "qk_layernorm": false,
            "add_bias_linear": false,
            "add_qkv_bias": false,
            "bias_activation_fusion": false,
            "gated_linear_unit": true,
            "init_method_std": 0.01,
            "attention_softmax_in_fp32": true,
            "masked_softmax_fusion": false,
            "layernorm_zero_centered_gamma": false,
            "bias_dropout_fusion":false,
            "apply_rope_fusion": false,
            "memory_efficient_layer_norm": false,
            "max_position_embeddings": 4096,
            "fp16": false,
            "bf16": true,
            "params_dtype": "bf16",
            "fp16_lm_cross_entropy": false,
            "rotary_percent": 1.0,
            "rotary_base":100000,
            "position_embedding_type": "rope",
            "use_fused_rotary_pos_emb": false,
            "rope_scaling": null,
            "parallel_output": true,
            "initializer_factor": 1.0,
            "activation_func": "silu",
            "vocab_size": 92553,
            "rope_theta": 1000000.0,
            "is_encoder_decoder": false
        },
        "image_encoder": {
            "vision_encoder": {
                "model_id": "InternViT",
                "num_layers": 24,
                "hidden_size": 1024,
                "ffn_hidden_size": 4096,
                "num_attention_heads": 16,
                "num_channels": 3,
                "patch_size": 14,
                "image_size": 448,
                "add_qkv_bias": true,
                "qk_layernorm": false,
                "activation_func": "gelu",
                "normalization": "LayerNorm",
                "layernorm_epsilon": 1e-6,
                "hidden_dropout": 0.0,
                "drop_path_rate": 0.0,
                "attention_dropout": 0.0,
                "init_method_std": 0.02,
                "initializer_factor": 1.0,
                "output_hidden_states": false,
                "use_return_dict": false,
                "params_dtype": "bf16",
                "post_layer_norm": false,
                "downsample_ratio": 0.5,
                "fp16": false,
                "bf16": true,
                "attention_softmax_in_fp32": false,
                "select_layer": -1,
                "ps_version": "v2",
                "freeze": true
            },
            "vision_projector": {
                "model_id": "InternVLMLP",
                "downsample_ratio": 0.5,
                "vit_hidden_size": 1024,
                "llm_hidden_size": 2048
            }
        },
        "tokenizer":{
            "hub_backend": "hf",
            "autotokenizer_name": "AutoTokenizer",
            "from_pretrained": "/home/ma-user/work/models/InternVL2_5-2B",
            "add_eos_token": false,
            "use_fast": false
        },
        "generation_config":{
            "do_sample": false,
            "bos_token_id": 1,
            "eos_token_id": 92542,
            "pad_token_id": 2,
            "max_length": 4096,
            "max_new_tokens": 4096,
            "temperature": 1.0,
            "output_attentions":false,
            "output_hidden_states":false,
            "use_cache":false,
            "decoder_start_token_id":null,
            "min_new_tokens":null,
            "min_length":0,
            "constraints":null,
            "num_beams":1,
            "force_words_ids":null,
            "top_k":50,
            "top_p":1.0,
            "prompt_lookup_num_tokens":null,
            "guidance_scale":null,
            "bad_words_ids": null,
            "begin_suppress_tokens": null,
            "diversity_penalty": 0.0,
            "early_stopping": false,
            "encoder_no_repeat_ngram_size": 0,
            "encoder_repetition_penalty": 1.0,
            "epsilon_cutoff": 0.0,
            "eta_cutoff": 0.0,
            "exponential_decay_length_penalty": null,
            "forced_bos_token_id": null,
            "forced_decoder_ids": null,
            "forced_eos_token_id": null,
            "length_penalty": 1.0,
            "low_memory": null,
            "max_time": null,
            "no_repeat_ngram_size": 0,
            "num_assistant_tokens": 5,
            "num_assistant_tokens_schedule": "heuristic",
            "num_beam_groups": 1,
            "num_return_sequences": 1,
            "output_scores": false,
            "penalty_alpha": null,
            "remove_invalid_values": false,
            "renormalize_logits": false,
            "repetition_penalty": 1.0,
            "return_dict_in_generate": false,
            "sequence_bias": null,
            "suppress_tokens": null,
            "typical_p": 1.0
          },
          "text_encoder": null,
          "video_encoder": null
        }
    ```
    
4. tp/pp均未成功尝试，报错显示pp出现

# 训练迁移

**训练小问题1：若直接运行下面训练脚本**

```bash
bash examples/internvl2.5/finetune_internvl2.5_2B.sh 2>&1 | tee train_logs/$(date '+%Y-%m-%d_%H-%M-%S').log

# 报错下面信息
RuntimeError: The Inner error is reported as above. The process exits for this inner error, and the current working operator name is HcclAllreduce.
Since the operator is called asynchronously, the stacktrace may be inaccurate. If you want to get the accurate stacktrace, pleace set the environment variable ASCEND_LAUNCH_BLOCKING=1.
```

解决方法如下

```bash
# 在脚本中指定命令参数ASCEND_LAUNCH_BLOCKING=1，强制将异步操作改为同步执行
ASCEND_LAUNCH_BLOCKING=1 bash examples/internvl2.5/finetune_internvl2.5_2B.sh 2>&1 | tee train_logs/$(date '+%Y-%m-%d_%H-%M-%S').log
```

~~但是可能这样操作会影响训练的性能，后续待解决~~

实际是因为爆显存导致的不同步，不应当使用BLOCKING

**训练小问题2：在新的机器上报错**

```bash
# 得到报错信息
RuntimeError: create:build/CMakeFiles/torch_npu.dir/compiler_depend.ts:91 HCCL function error: HcclCommInitRootInfo(numRanks, &rootInfo, rank, &(comm->hcclComm_)), error code is 7
```

直接把脚本中的运行NPU数，pp数改为1，因为新机器上只有1张NPU

# 杂项

### 用户隔离

`/home/ma-user/work/<username>/` 作为各子用户的HOME目录，其下的 `init.sh` 作为登陆入口

```
Host ict
  HostName dev-modelarts.cn-southwest-2.huaweicloud.com
  User ma-user
  Port 30998
  RemoteCommand /home/ma-user/work/<username>/init.sh
  RequestTTY yes
```

VS Code使用自己的终端

<aside>
⚠️

一定要在自己的项目文件夹中设置，否则会和其他人的混在一起

</aside>

打开远程项目文件夹（例如 `~/MindSpeed-MM`），打开**工作区设置（JSON）**，写入如下内容

```json
{
    "terminal.integrated.profiles.linux": {
        "zsh (wzx)": {
            "path": "/home/ma-user/work/wzx/init.sh",
        },
        "bash": {
            "path": "bash",
            "icon": "terminal-bash"
        },
        "zsh": {
            "path": "zsh"
        },
        "fish": {
            "path": "fish"
        },
        "tmux": {
            "path": "tmux",
            "icon": "terminal-tmux"
        },
        "pwsh": {
            "path": "pwsh",
            "icon": "terminal-powershell"
        }
    },
    "terminal.integrated.defaultProfile.linux": "zsh (wzx)",
}
```

### CA证书问题

由于服务器上的CA根证书仅root可读，导致curl、git等会出错。我下载了curl官方提供的ca-bundle文件到 `/home/ma-user/work/.local/share/cacert.pem` ，导入如下环境变量可以修复问题。

```bash
# CA Bundle
export CURL_CA_BUNDLE=~/../.local/share/certs/cacert.pem
export GIT_SSL_CAINFO=~/../.local/share/certs/cacert.pem
export SSL_CERT_FILE=~/../.local/share/certs/cacert.pem
```

### 本地编译安装了一些东西

在 `/home/ma-user/work/.local/bin` 

- zsh
- zellij
- btm
- [kzombie.sh](http://kzombie.sh)：快速杀死所有占用NPU的进程

### 最终环境

- `uv pip list`
    
    ```prolog
    ➜  MindSpeed-MM git:(master) ✗ uv pip list
    Package                   Version     Editable project location
    ------------------------- ----------- ---------------------------------------------
    accelerate                0.32.1
    aiohappyeyeballs          2.5.0
    aiohttp                   3.11.13
    aiosignal                 1.3.2
    annotated-types           0.7.0
    antlr4-python3-runtime    4.9.3
    apex                      0.1+ascend
    async-timeout             5.0.1
    attrs                     25.1.0
    av                        14.2.0
    beartype                  0.20.0
    beautifulsoup4            4.13.3
    bs4                       0.0.2
    certifi                   2025.1.31
    charset-normalizer        3.4.1
    datasets                  3.3.2
    decorator                 5.2.1
    decord                    0.6.0
    diffusers                 0.30.3
    dill                      0.3.8
    distro                    1.9.0
    docstring-parser          0.16
    einops                    0.8.1
    exceptiongroup            1.2.2
    filelock                  3.17.0
    frozenlist                1.5.0
    fsspec                    2024.12.0
    ftfy                      6.3.1
    gpytorch                  1.14
    greenlet                  3.1.1
    huggingface-hub           0.29.3
    idna                      3.10
    imageio                   2.37.0
    imageio-ffmpeg            0.6.0
    importlib-metadata        8.6.1
    importlib-resources       6.5.2
    iniconfig                 2.0.0
    jaxtyping                 0.2.38
    jinja2                    3.1.6
    joblib                    1.4.2
    jsonargparse              4.37.0
    jsonnet                   0.20.0
    jsonschema                4.23.0
    jsonschema-specifications 2024.10.1
    linear-operator           0.6
    markupsafe                3.0.2
    mindspeed                 0.8.0       /home/ma-user/work/wzx/MindSpeed-MM/MindSpeed
    mindspeed-mm              0.1         /home/ma-user/work/wzx/MindSpeed-MM
    mpmath                    1.3.0
    multidict                 6.1.0
    multiprocess              0.70.16
    networkx                  3.4.2
    ninja                     1.11.1.3
    numpy                     1.26.4
    omegaconf                 2.3.0
    packaging                 24.2
    pandarallel               1.6.5
    pandas                    2.0.3
    peft                      0.7.1
    pillow                    11.1.0
    pluggy                    1.5.0
    propcache                 0.3.0
    protobuf                  6.30.0
    psutil                    7.0.0
    pyarrow                   19.0.1
    pybind11                  2.13.6
    pydantic                  2.10.6
    pydantic-core             2.27.2
    pytest                    8.3.5
    python-dateutil           2.9.0.post0
    python-json-logger        3.3.0
    pytz                      2025.1
    pyyaml                    6.0.2
    qwen-vl-utils             0.0.10
    reconplogger              4.17.1
    referencing               0.36.2
    regex                     2024.11.6
    requests                  2.32.3
    rpds-py                   0.23.1
    ruyaml                    0.91.0
    safetensors               0.5.3
    scikit-learn              1.6.1
    scipy                     1.15.2
    sentencepiece             0.2.0
    setuptools                65.7.0
    six                       1.17.0
    soupsieve                 2.6
    sqlalchemy                2.0.38
    sympy                     1.13.3
    threadpoolctl             3.5.0
    timm                      1.0.8
    tokenizers                0.20.3
    toml                      0.10.2
    tomli                     2.2.1
    torch                     2.1.0
    torch-npu                 2.1.0.post8
    torchvision               0.16.0
    tqdm                      4.67.1
    transformers              4.45.0
    typeshed-client           2.7.0
    typing-extensions         4.12.2
    tzdata                    2025.1
    urllib3                   2.3.0
    wadler-lindig             0.1.3
    wcwidth                   0.2.13
    wheel                     0.45.1
    xxhash                    3.5.0
    yarl                      1.18.3
    zipp                      3.21.0
    ```
    

### 2B finetune

```bash
#!/bin/bash
source /usr/local/Ascend/ascend-toolkit/set_env.sh
export ASCEND_SLOG_PRINT_TO_STDOUT=0
export ASCEND_GLOBAL_LOG_LEVEL=3
export TASK_QUEUE_ENABLE=2
export COMBINED_ENABLE=1
export CPU_AFFINITY_CONF=1
export HCCL_CONNECT_TIMEOUT=1200
export CUDA_DEVICE_MAX_CONNECTIONS=1
export PYTORCH_NPU_ALLOC_CONF=expandable_segments:True
export ACLNN_CACHE_LIMIT=100000

echo "begin!"

NPUS_PER_NODE=2
MASTER_ADDR=localhost
MASTER_PORT=10001
NNODES=1
NODE_RANK=0
WORLD_SIZE=$(($NPUS_PER_NODE*$NNODES))

MBS=2
GRAD_ACC_STEP=1
TP=1
PP=1
CP=1
DP=$(($WORLD_SIZE/$TP/$PP/$CP))
GBS=$(($MBS*$GRAD_ACC_STEP*$DP))

MM_DATA="./examples/internvl2.5/data_2B_video.json"
MM_MODEL="./examples/internvl2.5/model_2B.json"
MM_TOOL="./mindspeed_mm/tools/tools.json"
LOAD_PATH="/home/ma-user/work/models_ms/InternVL2_5-2B"
SAVE_PATH="save_dir"

MM_ARGS="
    --mm-data ${MM_DATA} \
    --mm-model ${MM_MODEL} \
    --mm-tool ${MM_TOOL}
"

DISTRIBUTED_ARGS="
    --nproc_per_node $NPUS_PER_NODE \
    --nnodes $NNODES \
    --node_rank $NODE_RANK \
    --master_addr $MASTER_ADDR \
    --master_port $MASTER_PORT
"

GPT_ARGS="
    --tensor-model-parallel-size ${TP} \
    --pipeline-model-parallel-size ${PP} \
    --context-parallel-size ${CP} \
    --micro-batch-size ${MBS} \
    --global-batch-size ${GBS} \
    --seq-length 4096 \
    --tokenizer-type NullTokenizer \
    --vocab-size 92553 \
    --position-embedding-type rope \
    --rotary-base 1000000 \
    --swiglu \
    --no-masked-softmax-fusion \
    --lr 4e-5 \
    --min-lr 0.0 \
    --train-iters 5000 \
    --lr-decay-style cosine \
    --weight-decay 0.05 \
    --clip-grad 1.0 \
    --adam-beta1 0.9 \
    --adam-beta2 0.999 \
    --no-gradient-accumulation-fusion \
    --no-load-optim \
    --no-load-rng \
    --no-save-optim \
    --no-save-rng \
    --use-distributed-optimizer \
    --bf16 \
    --load $LOAD_PATH \
    --variable-seq-lengths \
    --normalization RMSNorm \
    --num-workers 4 \
    --trust-remote-code \
    --use_flash_attn \
    --overlap_grad_reduce \
    --overlap_grad_reduce True \
    --overlap_p2p_comm True \
"

OUTPUT_ARGS="
    --log-interval 1 \
    --save-interval 5000 \
    --eval-interval 5000 \
    --eval-iters 5000 \
    --save $SAVE_PATH \
"

logfile=$(date +%Y%m%d)_$(date +%H%M%S)
mkdir -p logs
torchrun $DISTRIBUTED_ARGS \
    pretrain_internvl.py \
    $GPT_ARGS \
    $MM_ARGS \
    $OUTPUT_ARGS \
    --swap-attention \
    --distributed-backend nccl \
    | tee logs/train_${logfile}.log 2>&1
chmod 440 logs/train_${logfile}.log

#     --recompute-granularity full \
#     --recompute-method uniform \
#     --recompute-num-layers 1 \
#     --recompute-activations
```

### InternVL2.5-8B原模型（hf）

```bash
InternVLChatModel(
  (vision_model): InternVisionModel(
    (embeddings): InternVisionEmbeddings(
      (patch_embedding): Conv2d(3, 1024, kernel_size=(14, 14), stride=(14, 14))
    )
    (encoder): InternVisionEncoder(
      (layers): ModuleList(
        (0-23): 24 x InternVisionEncoderLayer(
          (attn): InternAttention(
            (qkv): Linear(in_features=1024, out_features=3072, bias=True)
            (attn_drop): Dropout(p=0.0, inplace=False)
            (proj_drop): Dropout(p=0.0, inplace=False)
            (proj): Linear(in_features=1024, out_features=1024, bias=True)
          )
          (mlp): InternMLP(
            (act): GELUActivation()
            (fc1): Linear(in_features=1024, out_features=4096, bias=True)
            (fc2): Linear(in_features=4096, out_features=1024, bias=True)
          )
          (norm1): LayerNorm((1024,), eps=1e-06, elementwise_affine=True)
          (norm2): LayerNorm((1024,), eps=1e-06, elementwise_affine=True)
          (drop_path1): Identity()
          (drop_path2): Identity()
        )
      )
    )
  )
  (language_model): InternLM2ForCausalLM(
    (model): InternLM2Model(
      (tok_embeddings): Embedding(92553, 4096, padding_idx=2)
      (layers): ModuleList(
        (0-31): 32 x InternLM2DecoderLayer(
          (attention): InternLM2Attention(
            (wqkv): Linear(in_features=4096, out_features=6144, bias=False)
            (wo): Linear(in_features=4096, out_features=4096, bias=False)
            (rotary_emb): InternLM2DynamicNTKScalingRotaryEmbedding()
          )
          (feed_forward): InternLM2MLP(
            (w1): Linear(in_features=4096, out_features=14336, bias=False)
            (w3): Linear(in_features=4096, out_features=14336, bias=False)
            (w2): Linear(in_features=14336, out_features=4096, bias=False)
            (act_fn): SiLU()
          )
          (attention_norm): InternLM2RMSNorm()
          (ffn_norm): InternLM2RMSNorm()
        )
      )
      (norm): InternLM2RMSNorm()
    )
    (output): Linear(in_features=4096, out_features=92553, bias=False)
  )
  (mlp1): Sequential(
    (0): LayerNorm((4096,), eps=1e-05, elementwise_affine=True)
    (1): Linear(in_features=4096, out_features=4096, bias=True)
    (2): GELU(approximate='none')
    (3): Linear(in_features=4096, out_features=4096, bias=True)
  )
)
```

`model.safetensors.index.json` 

```bash
{
  "metadata": {
    "total_size": 16150730752
  },
  "weight_map": {
    "language_model.model.layers.0.attention.wo.weight": "model-00001-of-00004.safetensors",
    "language_model.model.layers.0.attention.wqkv.weight": "model-00001-of-00004.safetensors",
    "language_model.model.layers.0.attention_norm.weight": "model-00001-of-00004.safetensors",
    "language_model.model.layers.0.feed_forward.w1.weight": "model-00001-of-00004.safetensors",
    "language_model.model.layers.0.feed_forward.w2.weight": "model-00001-of-00004.safetensors",
    "language_model.model.layers.0.feed_forward.w3.weight": "model-00001-of-00004.safetensors",
    "language_model.model.layers.0.ffn_norm.weight": "model-00001-of-00004.safetensors",
    "language_model.model.layers.1.attention.wo.weight": "model-00001-of-00004.safetensors",
    "language_model.model.layers.1.attention.wqkv.weight": "model-00001-of-00004.safetensors",
    "language_model.model.layers.1.attention_norm.weight": "model-00001-of-00004.safetensors",
    "language_model.model.layers.1.feed_forward.w1.weight": "model-00001-of-00004.safetensors",
    "language_model.model.layers.1.feed_forward.w2.weight": "model-00001-of-00004.safetensors",
    "language_model.model.layers.1.feed_forward.w3.weight": "model-00001-of-00004.safetensors",
    "language_model.model.layers.1.ffn_norm.weight": "model-00001-of-00004.safetensors",
    "language_model.model.layers.10.attention.wo.weight": "model-00002-of-00004.safetensors",
    "language_model.model.layers.10.attention.wqkv.weight": "model-00002-of-00004.safetensors",
    "language_model.model.layers.10.attention_norm.weight": "model-00002-of-00004.safetensors",
    "language_model.model.layers.10.feed_forward.w1.weight": "model-00002-of-00004.safetensors",
    "language_model.model.layers.10.feed_forward.w2.weight": "model-00002-of-00004.safetensors",
    "language_model.model.layers.10.feed_forward.w3.weight": "model-00002-of-00004.safetensors",
    "language_model.model.layers.10.ffn_norm.weight": "model-00002-of-00004.safetensors",
    "language_model.model.layers.11.attention.wo.weight": "model-00002-of-00004.safetensors",
    "language_model.model.layers.11.attention.wqkv.weight": "model-00002-of-00004.safetensors",
    "language_model.model.layers.11.attention_norm.weight": "model-00002-of-00004.safetensors",
    "language_model.model.layers.11.feed_forward.w1.weight": "model-00002-of-00004.safetensors",
    "language_model.model.layers.11.feed_forward.w2.weight": "model-00002-of-00004.safetensors",
    "language_model.model.layers.11.feed_forward.w3.weight": "model-00002-of-00004.safetensors",
    "language_model.model.layers.11.ffn_norm.weight": "model-00002-of-00004.safetensors",
    "language_model.model.layers.12.attention.wo.weight": "model-00002-of-00004.safetensors",
    "language_model.model.layers.12.attention.wqkv.weight": "model-00002-of-00004.safetensors",
    "language_model.model.layers.12.attention_norm.weight": "model-00002-of-00004.safetensors",
    "language_model.model.layers.12.feed_forward.w1.weight": "model-00002-of-00004.safetensors",
    "language_model.model.layers.12.feed_forward.w2.weight": "model-00002-of-00004.safetensors",
    "language_model.model.layers.12.feed_forward.w3.weight": "model-00002-of-00004.safetensors",
    "language_model.model.layers.12.ffn_norm.weight": "model-00002-of-00004.safetensors",
    "language_model.model.layers.13.attention.wo.weight": "model-00002-of-00004.safetensors",
    "language_model.model.layers.13.attention.wqkv.weight": "model-00002-of-00004.safetensors",
    "language_model.model.layers.13.attention_norm.weight": "model-00002-of-00004.safetensors",
    "language_model.model.layers.13.feed_forward.w1.weight": "model-00002-of-00004.safetensors",
    "language_model.model.layers.13.feed_forward.w2.weight": "model-00002-of-00004.safetensors",
    "language_model.model.layers.13.feed_forward.w3.weight": "model-00002-of-00004.safetensors",
    "language_model.model.layers.13.ffn_norm.weight": "model-00002-of-00004.safetensors",
    "language_model.model.layers.14.attention.wo.weight": "model-00002-of-00004.safetensors",
    "language_model.model.layers.14.attention.wqkv.weight": "model-00002-of-00004.safetensors",
    "language_model.model.layers.14.attention_norm.weight": "model-00002-of-00004.safetensors",
    "language_model.model.layers.14.feed_forward.w1.weight": "model-00002-of-00004.safetensors",
    "language_model.model.layers.14.feed_forward.w2.weight": "model-00002-of-00004.safetensors",
    "language_model.model.layers.14.feed_forward.w3.weight": "model-00002-of-00004.safetensors",
    "language_model.model.layers.14.ffn_norm.weight": "model-00002-of-00004.safetensors",
    "language_model.model.layers.15.attention.wo.weight": "model-00002-of-00004.safetensors",
    "language_model.model.layers.15.attention.wqkv.weight": "model-00002-of-00004.safetensors",
    "language_model.model.layers.15.attention_norm.weight": "model-00002-of-00004.safetensors",
    "language_model.model.layers.15.feed_forward.w1.weight": "model-00002-of-00004.safetensors",
    "language_model.model.layers.15.feed_forward.w2.weight": "model-00002-of-00004.safetensors",
    "language_model.model.layers.15.feed_forward.w3.weight": "model-00002-of-00004.safetensors",
    "language_model.model.layers.15.ffn_norm.weight": "model-00002-of-00004.safetensors",
    "language_model.model.layers.16.attention.wo.weight": "model-00002-of-00004.safetensors",
    "language_model.model.layers.16.attention.wqkv.weight": "model-00002-of-00004.safetensors",
    "language_model.model.layers.16.attention_norm.weight": "model-00002-of-00004.safetensors",
    "language_model.model.layers.16.feed_forward.w1.weight": "model-00002-of-00004.safetensors",
    "language_model.model.layers.16.feed_forward.w2.weight": "model-00002-of-00004.safetensors",
    "language_model.model.layers.16.feed_forward.w3.weight": "model-00002-of-00004.safetensors",
    "language_model.model.layers.16.ffn_norm.weight": "model-00002-of-00004.safetensors",
    "language_model.model.layers.17.attention.wo.weight": "model-00002-of-00004.safetensors",
    "language_model.model.layers.17.attention.wqkv.weight": "model-00002-of-00004.safetensors",
    "language_model.model.layers.17.attention_norm.weight": "model-00002-of-00004.safetensors",
    "language_model.model.layers.17.feed_forward.w1.weight": "model-00002-of-00004.safetensors",
    "language_model.model.layers.17.feed_forward.w2.weight": "model-00002-of-00004.safetensors",
    "language_model.model.layers.17.feed_forward.w3.weight": "model-00002-of-00004.safetensors",
    "language_model.model.layers.17.ffn_norm.weight": "model-00002-of-00004.safetensors",
    "language_model.model.layers.18.attention.wo.weight": "model-00002-of-00004.safetensors",
    "language_model.model.layers.18.attention.wqkv.weight": "model-00002-of-00004.safetensors",
    "language_model.model.layers.18.attention_norm.weight": "model-00002-of-00004.safetensors",
    "language_model.model.layers.18.feed_forward.w1.weight": "model-00002-of-00004.safetensors",
    "language_model.model.layers.18.feed_forward.w2.weight": "model-00002-of-00004.safetensors",
    "language_model.model.layers.18.feed_forward.w3.weight": "model-00002-of-00004.safetensors",
    "language_model.model.layers.18.ffn_norm.weight": "model-00002-of-00004.safetensors",
    "language_model.model.layers.19.attention.wo.weight": "model-00002-of-00004.safetensors",
    "language_model.model.layers.19.attention.wqkv.weight": "model-00002-of-00004.safetensors",
    "language_model.model.layers.19.attention_norm.weight": "model-00003-of-00004.safetensors",
    "language_model.model.layers.19.feed_forward.w1.weight": "model-00002-of-00004.safetensors",
    "language_model.model.layers.19.feed_forward.w2.weight": "model-00003-of-00004.safetensors",
    "language_model.model.layers.19.feed_forward.w3.weight": "model-00003-of-00004.safetensors",
    "language_model.model.layers.19.ffn_norm.weight": "model-00003-of-00004.safetensors",
    "language_model.model.layers.2.attention.wo.weight": "model-00001-of-00004.safetensors",
    "language_model.model.layers.2.attention.wqkv.weight": "model-00001-of-00004.safetensors",
    "language_model.model.layers.2.attention_norm.weight": "model-00001-of-00004.safetensors",
    "language_model.model.layers.2.feed_forward.w1.weight": "model-00001-of-00004.safetensors",
    "language_model.model.layers.2.feed_forward.w2.weight": "model-00001-of-00004.safetensors",
    "language_model.model.layers.2.feed_forward.w3.weight": "model-00001-of-00004.safetensors",
    "language_model.model.layers.2.ffn_norm.weight": "model-00001-of-00004.safetensors",
    "language_model.model.layers.20.attention.wo.weight": "model-00003-of-00004.safetensors",
    "language_model.model.layers.20.attention.wqkv.weight": "model-00003-of-00004.safetensors",
    "language_model.model.layers.20.attention_norm.weight": "model-00003-of-00004.safetensors",
    "language_model.model.layers.20.feed_forward.w1.weight": "model-00003-of-00004.safetensors",
    "language_model.model.layers.20.feed_forward.w2.weight": "model-00003-of-00004.safetensors",
    "language_model.model.layers.20.feed_forward.w3.weight": "model-00003-of-00004.safetensors",
    "language_model.model.layers.20.ffn_norm.weight": "model-00003-of-00004.safetensors",
    "language_model.model.layers.21.attention.wo.weight": "model-00003-of-00004.safetensors",
    "language_model.model.layers.21.attention.wqkv.weight": "model-00003-of-00004.safetensors",
    "language_model.model.layers.21.attention_norm.weight": "model-00003-of-00004.safetensors",
    "language_model.model.layers.21.feed_forward.w1.weight": "model-00003-of-00004.safetensors",
    "language_model.model.layers.21.feed_forward.w2.weight": "model-00003-of-00004.safetensors",
    "language_model.model.layers.21.feed_forward.w3.weight": "model-00003-of-00004.safetensors",
    "language_model.model.layers.21.ffn_norm.weight": "model-00003-of-00004.safetensors",
    "language_model.model.layers.22.attention.wo.weight": "model-00003-of-00004.safetensors",
    "language_model.model.layers.22.attention.wqkv.weight": "model-00003-of-00004.safetensors",
    "language_model.model.layers.22.attention_norm.weight": "model-00003-of-00004.safetensors",
    "language_model.model.layers.22.feed_forward.w1.weight": "model-00003-of-00004.safetensors",
    "language_model.model.layers.22.feed_forward.w2.weight": "model-00003-of-00004.safetensors",
    "language_model.model.layers.22.feed_forward.w3.weight": "model-00003-of-00004.safetensors",
    "language_model.model.layers.22.ffn_norm.weight": "model-00003-of-00004.safetensors",
    "language_model.model.layers.23.attention.wo.weight": "model-00003-of-00004.safetensors",
    "language_model.model.layers.23.attention.wqkv.weight": "model-00003-of-00004.safetensors",
    "language_model.model.layers.23.attention_norm.weight": "model-00003-of-00004.safetensors",
    "language_model.model.layers.23.feed_forward.w1.weight": "model-00003-of-00004.safetensors",
    "language_model.model.layers.23.feed_forward.w2.weight": "model-00003-of-00004.safetensors",
    "language_model.model.layers.23.feed_forward.w3.weight": "model-00003-of-00004.safetensors",
    "language_model.model.layers.23.ffn_norm.weight": "model-00003-of-00004.safetensors",
    "language_model.model.layers.24.attention.wo.weight": "model-00003-of-00004.safetensors",
    "language_model.model.layers.24.attention.wqkv.weight": "model-00003-of-00004.safetensors",
    "language_model.model.layers.24.attention_norm.weight": "model-00003-of-00004.safetensors",
    "language_model.model.layers.24.feed_forward.w1.weight": "model-00003-of-00004.safetensors",
    "language_model.model.layers.24.feed_forward.w2.weight": "model-00003-of-00004.safetensors",
    "language_model.model.layers.24.feed_forward.w3.weight": "model-00003-of-00004.safetensors",
    "language_model.model.layers.24.ffn_norm.weight": "model-00003-of-00004.safetensors",
    "language_model.model.layers.25.attention.wo.weight": "model-00003-of-00004.safetensors",
    "language_model.model.layers.25.attention.wqkv.weight": "model-00003-of-00004.safetensors",
    "language_model.model.layers.25.attention_norm.weight": "model-00003-of-00004.safetensors",
    "language_model.model.layers.25.feed_forward.w1.weight": "model-00003-of-00004.safetensors",
    "language_model.model.layers.25.feed_forward.w2.weight": "model-00003-of-00004.safetensors",
    "language_model.model.layers.25.feed_forward.w3.weight": "model-00003-of-00004.safetensors",
    "language_model.model.layers.25.ffn_norm.weight": "model-00003-of-00004.safetensors",
    "language_model.model.layers.26.attention.wo.weight": "model-00003-of-00004.safetensors",
    "language_model.model.layers.26.attention.wqkv.weight": "model-00003-of-00004.safetensors",
    "language_model.model.layers.26.attention_norm.weight": "model-00003-of-00004.safetensors",
    "language_model.model.layers.26.feed_forward.w1.weight": "model-00003-of-00004.safetensors",
    "language_model.model.layers.26.feed_forward.w2.weight": "model-00003-of-00004.safetensors",
    "language_model.model.layers.26.feed_forward.w3.weight": "model-00003-of-00004.safetensors",
    "language_model.model.layers.26.ffn_norm.weight": "model-00003-of-00004.safetensors",
    "language_model.model.layers.27.attention.wo.weight": "model-00003-of-00004.safetensors",
    "language_model.model.layers.27.attention.wqkv.weight": "model-00003-of-00004.safetensors",
    "language_model.model.layers.27.attention_norm.weight": "model-00003-of-00004.safetensors",
    "language_model.model.layers.27.feed_forward.w1.weight": "model-00003-of-00004.safetensors",
    "language_model.model.layers.27.feed_forward.w2.weight": "model-00003-of-00004.safetensors",
    "language_model.model.layers.27.feed_forward.w3.weight": "model-00003-of-00004.safetensors",
    "language_model.model.layers.27.ffn_norm.weight": "model-00003-of-00004.safetensors",
    "language_model.model.layers.28.attention.wo.weight": "model-00003-of-00004.safetensors",
    "language_model.model.layers.28.attention.wqkv.weight": "model-00003-of-00004.safetensors",
    "language_model.model.layers.28.attention_norm.weight": "model-00003-of-00004.safetensors",
    "language_model.model.layers.28.feed_forward.w1.weight": "model-00003-of-00004.safetensors",
    "language_model.model.layers.28.feed_forward.w2.weight": "model-00003-of-00004.safetensors",
    "language_model.model.layers.28.feed_forward.w3.weight": "model-00003-of-00004.safetensors",
    "language_model.model.layers.28.ffn_norm.weight": "model-00003-of-00004.safetensors",
    "language_model.model.layers.29.attention.wo.weight": "model-00003-of-00004.safetensors",
    "language_model.model.layers.29.attention.wqkv.weight": "model-00003-of-00004.safetensors",
    "language_model.model.layers.29.attention_norm.weight": "model-00003-of-00004.safetensors",
    "language_model.model.layers.29.feed_forward.w1.weight": "model-00003-of-00004.safetensors",
    "language_model.model.layers.29.feed_forward.w2.weight": "model-00003-of-00004.safetensors",
    "language_model.model.layers.29.feed_forward.w3.weight": "model-00003-of-00004.safetensors",
    "language_model.model.layers.29.ffn_norm.weight": "model-00003-of-00004.safetensors",
    "language_model.model.layers.3.attention.wo.weight": "model-00001-of-00004.safetensors",
    "language_model.model.layers.3.attention.wqkv.weight": "model-00001-of-00004.safetensors",
    "language_model.model.layers.3.attention_norm.weight": "model-00001-of-00004.safetensors",
    "language_model.model.layers.3.feed_forward.w1.weight": "model-00001-of-00004.safetensors",
    "language_model.model.layers.3.feed_forward.w2.weight": "model-00001-of-00004.safetensors",
    "language_model.model.layers.3.feed_forward.w3.weight": "model-00001-of-00004.safetensors",
    "language_model.model.layers.3.ffn_norm.weight": "model-00001-of-00004.safetensors",
    "language_model.model.layers.30.attention.wo.weight": "model-00003-of-00004.safetensors",
    "language_model.model.layers.30.attention.wqkv.weight": "model-00003-of-00004.safetensors",
    "language_model.model.layers.30.attention_norm.weight": "model-00004-of-00004.safetensors",
    "language_model.model.layers.30.feed_forward.w1.weight": "model-00003-of-00004.safetensors",
    "language_model.model.layers.30.feed_forward.w2.weight": "model-00004-of-00004.safetensors",
    "language_model.model.layers.30.feed_forward.w3.weight": "model-00003-of-00004.safetensors",
    "language_model.model.layers.30.ffn_norm.weight": "model-00004-of-00004.safetensors",
    "language_model.model.layers.31.attention.wo.weight": "model-00004-of-00004.safetensors",
    "language_model.model.layers.31.attention.wqkv.weight": "model-00004-of-00004.safetensors",
    "language_model.model.layers.31.attention_norm.weight": "model-00004-of-00004.safetensors",
    "language_model.model.layers.31.feed_forward.w1.weight": "model-00004-of-00004.safetensors",
    "language_model.model.layers.31.feed_forward.w2.weight": "model-00004-of-00004.safetensors",
    "language_model.model.layers.31.feed_forward.w3.weight": "model-00004-of-00004.safetensors",
    "language_model.model.layers.31.ffn_norm.weight": "model-00004-of-00004.safetensors",
    "language_model.model.layers.4.attention.wo.weight": "model-00001-of-00004.safetensors",
    "language_model.model.layers.4.attention.wqkv.weight": "model-00001-of-00004.safetensors",
    "language_model.model.layers.4.attention_norm.weight": "model-00001-of-00004.safetensors",
    "language_model.model.layers.4.feed_forward.w1.weight": "model-00001-of-00004.safetensors",
    "language_model.model.layers.4.feed_forward.w2.weight": "model-00001-of-00004.safetensors",
    "language_model.model.layers.4.feed_forward.w3.weight": "model-00001-of-00004.safetensors",
    "language_model.model.layers.4.ffn_norm.weight": "model-00001-of-00004.safetensors",
    "language_model.model.layers.5.attention.wo.weight": "model-00001-of-00004.safetensors",
    "language_model.model.layers.5.attention.wqkv.weight": "model-00001-of-00004.safetensors",
    "language_model.model.layers.5.attention_norm.weight": "model-00001-of-00004.safetensors",
    "language_model.model.layers.5.feed_forward.w1.weight": "model-00001-of-00004.safetensors",
    "language_model.model.layers.5.feed_forward.w2.weight": "model-00001-of-00004.safetensors",
    "language_model.model.layers.5.feed_forward.w3.weight": "model-00001-of-00004.safetensors",
    "language_model.model.layers.5.ffn_norm.weight": "model-00001-of-00004.safetensors",
    "language_model.model.layers.6.attention.wo.weight": "model-00001-of-00004.safetensors",
    "language_model.model.layers.6.attention.wqkv.weight": "model-00001-of-00004.safetensors",
    "language_model.model.layers.6.attention_norm.weight": "model-00001-of-00004.safetensors",
    "language_model.model.layers.6.feed_forward.w1.weight": "model-00001-of-00004.safetensors",
    "language_model.model.layers.6.feed_forward.w2.weight": "model-00001-of-00004.safetensors",
    "language_model.model.layers.6.feed_forward.w3.weight": "model-00001-of-00004.safetensors",
    "language_model.model.layers.6.ffn_norm.weight": "model-00001-of-00004.safetensors",
    "language_model.model.layers.7.attention.wo.weight": "model-00001-of-00004.safetensors",
    "language_model.model.layers.7.attention.wqkv.weight": "model-00001-of-00004.safetensors",
    "language_model.model.layers.7.attention_norm.weight": "model-00001-of-00004.safetensors",
    "language_model.model.layers.7.feed_forward.w1.weight": "model-00001-of-00004.safetensors",
    "language_model.model.layers.7.feed_forward.w2.weight": "model-00001-of-00004.safetensors",
    "language_model.model.layers.7.feed_forward.w3.weight": "model-00001-of-00004.safetensors",
    "language_model.model.layers.7.ffn_norm.weight": "model-00001-of-00004.safetensors",
    "language_model.model.layers.8.attention.wo.weight": "model-00001-of-00004.safetensors",
    "language_model.model.layers.8.attention.wqkv.weight": "model-00001-of-00004.safetensors",
    "language_model.model.layers.8.attention_norm.weight": "model-00002-of-00004.safetensors",
    "language_model.model.layers.8.feed_forward.w1.weight": "model-00002-of-00004.safetensors",
    "language_model.model.layers.8.feed_forward.w2.weight": "model-00002-of-00004.safetensors",
    "language_model.model.layers.8.feed_forward.w3.weight": "model-00002-of-00004.safetensors",
    "language_model.model.layers.8.ffn_norm.weight": "model-00002-of-00004.safetensors",
    "language_model.model.layers.9.attention.wo.weight": "model-00002-of-00004.safetensors",
    "language_model.model.layers.9.attention.wqkv.weight": "model-00002-of-00004.safetensors",
    "language_model.model.layers.9.attention_norm.weight": "model-00002-of-00004.safetensors",
    "language_model.model.layers.9.feed_forward.w1.weight": "model-00002-of-00004.safetensors",
    "language_model.model.layers.9.feed_forward.w2.weight": "model-00002-of-00004.safetensors",
    "language_model.model.layers.9.feed_forward.w3.weight": "model-00002-of-00004.safetensors",
    "language_model.model.layers.9.ffn_norm.weight": "model-00002-of-00004.safetensors",
    "language_model.model.norm.weight": "model-00004-of-00004.safetensors",
    "language_model.model.tok_embeddings.weight": "model-00001-of-00004.safetensors",
    "language_model.output.weight": "model-00004-of-00004.safetensors",
    "mlp1.0.bias": "model-00004-of-00004.safetensors",
    "mlp1.0.weight": "model-00004-of-00004.safetensors",
    "mlp1.1.bias": "model-00004-of-00004.safetensors",
    "mlp1.1.weight": "model-00004-of-00004.safetensors",
    "mlp1.3.bias": "model-00004-of-00004.safetensors",
    "mlp1.3.weight": "model-00004-of-00004.safetensors",
    "vision_model.embeddings.class_embedding": "model-00001-of-00004.safetensors",
    "vision_model.embeddings.patch_embedding.bias": "model-00001-of-00004.safetensors",
    "vision_model.embeddings.patch_embedding.weight": "model-00001-of-00004.safetensors",
    "vision_model.embeddings.position_embedding": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.0.attn.proj.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.0.attn.proj.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.0.attn.qkv.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.0.attn.qkv.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.0.ls1": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.0.ls2": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.0.mlp.fc1.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.0.mlp.fc1.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.0.mlp.fc2.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.0.mlp.fc2.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.0.norm1.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.0.norm1.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.0.norm2.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.0.norm2.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.1.attn.proj.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.1.attn.proj.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.1.attn.qkv.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.1.attn.qkv.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.1.ls1": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.1.ls2": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.1.mlp.fc1.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.1.mlp.fc1.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.1.mlp.fc2.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.1.mlp.fc2.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.1.norm1.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.1.norm1.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.1.norm2.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.1.norm2.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.10.attn.proj.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.10.attn.proj.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.10.attn.qkv.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.10.attn.qkv.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.10.ls1": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.10.ls2": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.10.mlp.fc1.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.10.mlp.fc1.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.10.mlp.fc2.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.10.mlp.fc2.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.10.norm1.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.10.norm1.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.10.norm2.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.10.norm2.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.11.attn.proj.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.11.attn.proj.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.11.attn.qkv.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.11.attn.qkv.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.11.ls1": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.11.ls2": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.11.mlp.fc1.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.11.mlp.fc1.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.11.mlp.fc2.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.11.mlp.fc2.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.11.norm1.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.11.norm1.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.11.norm2.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.11.norm2.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.12.attn.proj.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.12.attn.proj.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.12.attn.qkv.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.12.attn.qkv.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.12.ls1": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.12.ls2": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.12.mlp.fc1.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.12.mlp.fc1.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.12.mlp.fc2.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.12.mlp.fc2.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.12.norm1.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.12.norm1.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.12.norm2.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.12.norm2.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.13.attn.proj.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.13.attn.proj.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.13.attn.qkv.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.13.attn.qkv.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.13.ls1": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.13.ls2": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.13.mlp.fc1.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.13.mlp.fc1.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.13.mlp.fc2.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.13.mlp.fc2.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.13.norm1.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.13.norm1.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.13.norm2.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.13.norm2.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.14.attn.proj.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.14.attn.proj.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.14.attn.qkv.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.14.attn.qkv.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.14.ls1": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.14.ls2": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.14.mlp.fc1.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.14.mlp.fc1.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.14.mlp.fc2.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.14.mlp.fc2.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.14.norm1.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.14.norm1.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.14.norm2.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.14.norm2.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.15.attn.proj.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.15.attn.proj.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.15.attn.qkv.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.15.attn.qkv.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.15.ls1": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.15.ls2": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.15.mlp.fc1.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.15.mlp.fc1.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.15.mlp.fc2.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.15.mlp.fc2.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.15.norm1.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.15.norm1.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.15.norm2.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.15.norm2.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.16.attn.proj.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.16.attn.proj.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.16.attn.qkv.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.16.attn.qkv.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.16.ls1": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.16.ls2": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.16.mlp.fc1.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.16.mlp.fc1.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.16.mlp.fc2.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.16.mlp.fc2.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.16.norm1.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.16.norm1.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.16.norm2.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.16.norm2.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.17.attn.proj.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.17.attn.proj.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.17.attn.qkv.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.17.attn.qkv.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.17.ls1": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.17.ls2": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.17.mlp.fc1.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.17.mlp.fc1.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.17.mlp.fc2.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.17.mlp.fc2.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.17.norm1.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.17.norm1.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.17.norm2.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.17.norm2.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.18.attn.proj.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.18.attn.proj.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.18.attn.qkv.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.18.attn.qkv.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.18.ls1": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.18.ls2": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.18.mlp.fc1.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.18.mlp.fc1.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.18.mlp.fc2.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.18.mlp.fc2.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.18.norm1.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.18.norm1.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.18.norm2.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.18.norm2.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.19.attn.proj.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.19.attn.proj.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.19.attn.qkv.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.19.attn.qkv.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.19.ls1": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.19.ls2": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.19.mlp.fc1.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.19.mlp.fc1.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.19.mlp.fc2.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.19.mlp.fc2.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.19.norm1.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.19.norm1.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.19.norm2.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.19.norm2.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.2.attn.proj.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.2.attn.proj.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.2.attn.qkv.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.2.attn.qkv.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.2.ls1": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.2.ls2": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.2.mlp.fc1.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.2.mlp.fc1.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.2.mlp.fc2.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.2.mlp.fc2.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.2.norm1.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.2.norm1.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.2.norm2.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.2.norm2.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.20.attn.proj.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.20.attn.proj.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.20.attn.qkv.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.20.attn.qkv.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.20.ls1": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.20.ls2": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.20.mlp.fc1.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.20.mlp.fc1.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.20.mlp.fc2.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.20.mlp.fc2.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.20.norm1.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.20.norm1.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.20.norm2.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.20.norm2.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.21.attn.proj.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.21.attn.proj.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.21.attn.qkv.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.21.attn.qkv.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.21.ls1": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.21.ls2": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.21.mlp.fc1.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.21.mlp.fc1.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.21.mlp.fc2.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.21.mlp.fc2.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.21.norm1.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.21.norm1.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.21.norm2.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.21.norm2.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.22.attn.proj.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.22.attn.proj.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.22.attn.qkv.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.22.attn.qkv.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.22.ls1": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.22.ls2": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.22.mlp.fc1.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.22.mlp.fc1.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.22.mlp.fc2.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.22.mlp.fc2.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.22.norm1.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.22.norm1.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.22.norm2.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.22.norm2.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.23.attn.proj.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.23.attn.proj.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.23.attn.qkv.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.23.attn.qkv.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.23.ls1": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.23.ls2": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.23.mlp.fc1.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.23.mlp.fc1.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.23.mlp.fc2.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.23.mlp.fc2.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.23.norm1.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.23.norm1.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.23.norm2.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.23.norm2.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.3.attn.proj.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.3.attn.proj.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.3.attn.qkv.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.3.attn.qkv.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.3.ls1": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.3.ls2": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.3.mlp.fc1.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.3.mlp.fc1.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.3.mlp.fc2.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.3.mlp.fc2.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.3.norm1.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.3.norm1.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.3.norm2.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.3.norm2.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.4.attn.proj.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.4.attn.proj.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.4.attn.qkv.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.4.attn.qkv.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.4.ls1": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.4.ls2": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.4.mlp.fc1.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.4.mlp.fc1.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.4.mlp.fc2.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.4.mlp.fc2.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.4.norm1.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.4.norm1.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.4.norm2.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.4.norm2.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.5.attn.proj.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.5.attn.proj.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.5.attn.qkv.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.5.attn.qkv.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.5.ls1": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.5.ls2": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.5.mlp.fc1.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.5.mlp.fc1.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.5.mlp.fc2.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.5.mlp.fc2.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.5.norm1.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.5.norm1.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.5.norm2.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.5.norm2.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.6.attn.proj.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.6.attn.proj.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.6.attn.qkv.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.6.attn.qkv.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.6.ls1": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.6.ls2": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.6.mlp.fc1.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.6.mlp.fc1.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.6.mlp.fc2.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.6.mlp.fc2.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.6.norm1.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.6.norm1.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.6.norm2.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.6.norm2.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.7.attn.proj.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.7.attn.proj.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.7.attn.qkv.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.7.attn.qkv.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.7.ls1": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.7.ls2": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.7.mlp.fc1.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.7.mlp.fc1.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.7.mlp.fc2.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.7.mlp.fc2.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.7.norm1.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.7.norm1.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.7.norm2.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.7.norm2.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.8.attn.proj.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.8.attn.proj.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.8.attn.qkv.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.8.attn.qkv.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.8.ls1": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.8.ls2": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.8.mlp.fc1.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.8.mlp.fc1.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.8.mlp.fc2.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.8.mlp.fc2.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.8.norm1.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.8.norm1.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.8.norm2.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.8.norm2.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.9.attn.proj.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.9.attn.proj.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.9.attn.qkv.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.9.attn.qkv.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.9.ls1": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.9.ls2": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.9.mlp.fc1.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.9.mlp.fc1.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.9.mlp.fc2.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.9.mlp.fc2.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.9.norm1.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.9.norm1.weight": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.9.norm2.bias": "model-00001-of-00004.safetensors",
    "vision_model.encoder.layers.9.norm2.weight": "model-00001-of-00004.safetensors"
  }
}
```

# 8B-inference.json

```json
{
  "infer_data_type": "video",
  "file_path": "/home/ma-user/work/cjj/red-panda.mp4",
  "prompts": "Please describe the video.",
  "pipeline_class": "InternVLPipeline",
  "from_pretrained": "/home/ma-user/work/cjj/saves/models/InternVL2_5-8B/release/mp_rank_00/model_optim_rng.pt",
  "template": "internvl2_5",
  "dtype": "bf16",
  "device": "npu",
  "pre_process": true,
  "post_process": true,
  "add_text_encoder": false,
  "img_embedding_idx": 1,
  "downsample_ratio": 0.5,
  "select_layer": -1,
  "ps_version": "v2",
  "add_rmsnorm_offset": false,
  "img_context_token_id": 92546,
  "num_segments": 8,
  "text_decoder": {
    "model_id": "internllm",
    "num_layers": 32,
    "hidden_size": 4096,
    "num_attention_heads": 32,
    "num_query_groups": 8,
    "ffn_hidden_size": 14336,
    "kv_channels": 128,
    "hidden_dropout": 0.0,
    "attention_dropout": 0.0,
    "layernorm_epsilon": 1e-6,
    "normalization": "RMSNorm",
    "qk_layernorm": false,
    "add_bias_linear": false,
    "add_qkv_bias": false,
    "bias_activation_fusion": false,
    "gated_linear_unit": true,
    "init_method_std": 0.01,
    "attention_softmax_in_fp32": true,
    "masked_softmax_fusion": false,
    "layernorm_zero_centered_gamma": false,
    "bias_dropout_fusion": false,
    "apply_rope_fusion": false,
    "memory_efficient_layer_norm": false,
    "max_position_embeddings": 32768,
    "fp16": false,
    "bf16": true,
    "params_dtype": "bf16",
    "fp16_lm_cross_entropy": false,
    "rotary_percent": 1.0,
    "position_embedding_type": "rope",
    "use_fused_rotary_pos_emb": false,
    "rope_scaling": null,
    "parallel_output": true,
    "initializer_factor": 1.0,
    "activation_func": "silu",
    "vocab_size": 92553,
    "rope_theta": 1000000.0,
    "rotary_base": 100000,
    "is_encoder_decoder": false
  },
  "image_encoder": {
    "vision_encoder": {
      "model_id": "InternViT",
      "num_layers": 24,
      "hidden_size": 1024,
      "ffn_hidden_size": 4096,
      "num_attention_heads": 16,
      "num_channels": 3,
      "patch_size": 14,
      "image_size": 448,
      "add_qkv_bias": true,
      "qk_layernorm": false,
      "activation_func": "gelu",
      "normalization": "LayerNorm",
      "layernorm_epsilon": 1e-6,
      "hidden_dropout": 0.0,
      "drop_path_rate": 0.0,
      "attention_dropout": 0.0,
      "init_method_std": 0.02,
      "initializer_factor": 1.0,
      "output_hidden_states": false,
      "use_return_dict": false,
      "params_dtype": "bf16",
      "post_layer_norm": false,
      "downsample_ratio": 0.5,
      "fp16": false,
      "bf16": true,
      "attention_softmax_in_fp32": false,
      "select_layer": -1,
      "ps_version": "v2",
      "freeze": true
    },
    "vision_projector": {
      "model_id": "InternVLMLP",
      "downsample_ratio": 0.5,
      "vit_hidden_size": 1024,
      "llm_hidden_size": 4096
    }
  },
  "tokenizer": {
    "hub_backend": "hf",
    "autotokenizer_name": "AutoTokenizer",
    "from_pretrained": "/home/ma-user/work/models/InternVL2_5-8B",
    "add_eos_token": false,
    "use_fast": false
  },
  "generation_config": {
    "do_sample": false,
    "bos_token_id": 1,
    "eos_token_id": 92542,
    "pad_token_id": null,
    "max_length": 20,
    "max_new_tokens": 1024,
    "temperature": 1.0,
    "output_attentions": false,
    "output_hidden_states": false,
    "use_cache": false,
    "decoder_start_token_id": null,
    "min_new_tokens": null,
    "min_length": 0,
    "constraints": null,
    "num_beams": 1,
    "force_words_ids": null,
    "top_k": 50,
    "top_p": 1.0,
    "prompt_lookup_num_tokens": null,
    "guidance_scale": null,
    "bad_words_ids": null,
    "begin_suppress_tokens": null,
    "diversity_penalty": 0.0,
    "early_stopping": false,
    "encoder_no_repeat_ngram_size": 0,
    "encoder_repetition_penalty": 1.0,
    "epsilon_cutoff": 0.0,
    "eta_cutoff": 0.0,
    "exponential_decay_length_penalty": null,
    "forced_bos_token_id": null,
    "forced_decoder_ids": null,
    "forced_eos_token_id": null,
    "length_penalty": 1.0,
    "low_memory": null,
    "max_time": null,
    "no_repeat_ngram_size": 0,
    "num_assistant_tokens": 5,
    "num_assistant_tokens_schedule": "heuristic",
    "num_beam_groups": 1,
    "num_return_sequences": 1,
    "output_scores": false,    
    "penalty_alpha": null,
    "remove_invalid_values": false,
    "renormalize_logits": false,
    "repetition_penalty": 1.0,
    "return_dict_in_generate": false,
    "sequence_bias": null,
    "suppress_tokens": null,
    "typical_p": 1.0
  },
  "text_encoder": null,
  "video_encoder": null
}
```

# model_8B.json

```json
{
  "model_id": "InternVL2.5",
  "pre_process": true,
  "post_process": true,
  "add_text_encoder": false,
  "img_embedding_idx": 1,
  "downsample_ratio": 0.5,
  "select_layer": -1,
  "ps_version": "v2",
  "add_rmsnorm_offset": false,
  "img_context_token_id": 92546,
  "text_decoder": {
    "model_id": "internllm",
    "num_layers": 32,
    "pipeline_num_layers": [32],
    "hidden_size": 4096,
    "kv_channels": 128,
    "num_attention_heads": 32,
    "num_query_groups": 8,
    "ffn_hidden_size": 14336,
    "hidden_dropout": 0.0,
    "attention_dropout": 0.0,
    "layernorm_epsilon": 1e-6,
    "normalization": "RMSNorm",
    "num_key_value_heads": 2,
    "add_bias_linear": false,
    "add_qkv_bias": false,
    "max_position_embeddings": 32768,
    "vocab_size": 92553,
    "rope_theta": 1000000.0,
    "rotary_base": 1000000,
    "rotary_percent": 1.0,
    "untie_embeddings_and_output_weights": true,
    "disable_bias_linear": true,
    "init_method_std": 0.02,
    "position_embedding_type": "rope",
    "activation_func": "silu",
    "attention_softmax_in_fp32": true,
    "use_fused_rotary_pos_emb": false,
    "params_dtype": "bf16",
    "bf16": true,
    "fp16_lm_cross_entropy": false,
    "parallel_output": true,
    "group_query_attention": true,
    "mrope_section": [16, 24, 24],
    "rope_scaling": null,
    "gated_linear_unit": true
  },
  "image_encoder": {
    "vision_encoder": {
      "model_id": "InternViT",
      "num_layers": 24,
      "pipeline_num_layers": [24],
      "hidden_size": 1024,
      "ffn_hidden_size": 4096,
      "num_attention_heads": 16,
      "num_channels": 3,
      "patch_size": 14,
      "image_size": 448,
      "add_qkv_bias": true,
      "qk_layernorm": false,
      "activation_func": "gelu",
      "normalization": "LayerNorm",
      "layernorm_epsilon": 1e-6,
      "hidden_dropout": 0.0,
      "drop_path_rate": 0.0,
      "attention_dropout": 0.0,
      "init_method_std": 0.02,
      "initializer_factor": 1.0,
      "output_hidden_states": false,
      "use_return_dict": false,
      "params_dtype": "bf16",
      "post_layer_norm": false,
      "downsample_ratio": 0.5,
      "fp16": false,
      "bf16": true,
      "attention_softmax_in_fp32": false,
      "select_layer": -1,
      "ps_version": "v2",
      "freeze": true
    },
    "vision_projector": {
      "model_id": "InternVLMLP",
      "downsample_ratio": 0.5,
      "vit_hidden_size": 1024,
      "llm_hidden_size": 4096
    }
  },
  "text_encoder": null,
  "video_encoder": null
}
```

# data_8B_video.json

```json
{
  "dataset_param": {
    "dataset_type": "multimodal",
    "basic_parameters": {
      "data_path": "/home/ma-user/work/dataset/dataset_A/dataset_A.jsonl",
      "data_folder": "/home/ma-user/work/dataset",
      "repeat_time": 1
    },
    "preprocess_parameters": {
      "image_reader_type": "torchvision",
      "train_pipeline": {
        "image": [
          {
            "trans_type": "Pad2Square",
            "param": { "mean": [0.485, 0.456, 0.406] }
          },
          {
            "trans_type": "Resize",
            "param": { "size": [448, 448], "interpolation": "BICUBIC" }
          },
          { "trans_type": "ToTensor" },
          {
            "trans_type": "norm_fun",
            "param": {
              "mean": [0.485, 0.456, 0.406],
              "std": [0.229, 0.224, 0.225]
            }
          }
        ]
      }
    },
    "tokenizer_config": {
      "hub_backend": "hf",
      "autotokenizer_name": "AutoTokenizer",
      "from_pretrained": "/home/ma-user/work/models/InternVL2_5-8B",
      "add_eos_token": false,
      "use_fast": false
    },
    "use_text_processer": true,
    "template_name": "internvl2_5",
    "patch_size": 14,
    "image_size": 448,
    "down_sample_ratio": 0.5,
    "group_by_length": true,
    "dynamic_image_size": true,
    "use_thumbnail": true,
    "min_dynamic_patch": 1,
    "max_dynamic_patch": 6,
    "min_num_frame": 4,
    "max_num_frame": 12,
    "sampling_method": "rand"
  },
  "dataloader_param": {
    "dataloader_mode": "sampler",
    "shuffle": true,
    "drop_last": true,
    "pin_memory": true,
    "sampler_type": "BaseRandomBatchSampler",
    "collate_param": { "model_name": "internvl", "pad_id": 2 }
  }
}
```

# Flash attn v2

BSND

[https://gitee.com/gp513/MindSpeed_1/blob/master/docs/ops/fusion_attention.md#flash_attention_v2-类的调用方式](https://gitee.com/gp513/MindSpeed_1/blob/master/docs/ops/fusion_attention.md#flash_attention_v2-%E7%B1%BB%E7%9A%84%E8%B0%83%E7%94%A8%E6%96%B9%E5%BC%8F)