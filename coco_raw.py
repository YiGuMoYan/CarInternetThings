import argparse
import sys
import yaml

import numpy as np
import tritonclient.http as httpclient

""" README.md
Python推理模型调用骨架
> 本代码框架为火山引擎边缘智能推理服务自动生成的模型调用骨架，采用Python编写。

Quick Start
> 注意python版本 >= 3.9

1. 安装依赖包

pip install numpy==1.24.2
pip install tritonclient\[http\]==2.32.0
pip install pyyaml==6.0

2. 调用代码
python main.py [-h] [--model_id MODEL_ID] [--server_url SERVER_URL]

--model_id: 模型ID
--server_url: 模型服务URL

3. 调用示例
python main.py
python main.py --model_id m-2100067825-8mnd8
python main.py --model_id m-2100067825-8mnd8 --server_url 127.0.01:30001
"""

# 模型配置信息
config_str = '''
model_id: m-official-13
server_url: 192.168.1.96:31000
model_name: COCO物体检测-01-SSD-ONNX
model_framework: ONNX
input:
    - name: input
      data_type: FP32
      dims: [1, 3, 512, 512]
output:
    - name: boxes
      data_type: FP32
      dims: [9, 5]
    - name: labels
      data_type: INT64
      dims: [9]

'''

# triton数据类型->numpy数据类型
type_dict = {
    'FP64': np.float64,
    'FP32': np.float32,
    'FP16': np.float16,
    'INT64': np.int64,
    'INT32': np.int32,
    'INT16': np.int16,
    'INT8': np.int8,
    'UINT64': np.uint64,
    'UINT32': np.uint32,
    'UINT16': np.uint16,
    'UINT8': np.uint8,
    'BOOL': np.bool_
}


# triton数据类型转换，返回np数据类型
def transfer_data_type(data_type):
    np_type = type_dict.get(data_type)
    return np_type


# 模型类，将配置文件转换成Python对象
class Model(object):
    def __init__(self, d):
        for a, b in d.items():
            if isinstance(b, (list, tuple)):
                setattr(self, a, [Model(x) if isinstance(x, dict) else x for x in b])
            else:
                setattr(self, a, Model(b) if isinstance(b, dict) else b)


# 根据文件路径加载yml配置文件
def load():
    model_config = yaml.load(config_str, Loader=yaml.Loader)
    return model_config


# 解析yml配置为Model对象
def parse_config(args):
    # 加载配置文件
    model_config = load()

    # 初始化Model
    model = Model(model_config)

    # args参数覆盖配置
    if args.model_id != "":
        model.model_id = args.model_id
    if args.server_url != "":
        model.server_url = args.server_url

    return model


# Mock输入结构
def mock_input(input):
    inputs = []
    for i in input:

        dims = i.dims
        if hasattr(i, 'reshape'):
            dims = i.reshape

        infer_input = httpclient.InferInput(i.name, dims, i.data_type)

        # Mock输入数据，通过numpy随机生成
        np_mock_data = np.random.uniform(0, 1, dims).astype(transfer_data_type(i.data_type))
        infer_input.set_data_from_numpy(np_mock_data, binary_data=False)

        inputs.append(infer_input)
    return inputs


# Mock输出结构
def mock_output(output):
    outputs = []
    for o in output:
        outputs.append(httpclient.InferRequestedOutput(o.name, binary_data=False))
    return outputs


# 程序入口
def main(args):
    # 从配置文件中解析参数
    model = parse_config(args)
    # 打印模型信息
    print("Model id : %s | name : %s | framework : %s" % (model.model_id, model.model_name, model.model_framework))

    # 使用Triton客户端调用脚本
    triton_client = httpclient.InferenceServerClient(url=model.server_url)
    results = triton_client.infer(model.model_id, inputs=mock_input(model.input), outputs=mock_output(model.output))

    # 打印结果
    print(results.get_output())


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Triton HTTP Client')
    parser.add_argument("--model_id", help="Inference Model Id", required=False, default="", type=str)
    parser.add_argument("--server_url", help="Inference Server HTTP URL", required=False, default="", type=str)
    args = parser.parse_args()

    sys.exit(main(args))