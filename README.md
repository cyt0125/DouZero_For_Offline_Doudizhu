# DouZero_For_Offline_Doudizhu: 将DouZero用于线下斗地主

*   本项目基于[DouZero](https://github.com/kwai/DouZero)
*   环境配置请移步项目DouZero
*   模型默认为WP，更换模型请修改start.py中的模型路径
*   运行main.py即可
*   SL (`baselines/sl/`): 基于人类数据进行深度学习的预训练模型
*   DouZero-ADP (`baselines/douzero_ADP/`): 以平均分数差异（Average Difference Points, ADP）为目标训练的Douzero智能体
*   DouZero-WP (`baselines/douzero_WP/`): 以胜率（Winning Percentage, WP）为目标训练的Douzero智能体

## 使用步骤
1. 打开ddzpy.py，运行即可开始
2. 选择玩家收到的牌和地主牌，以及地主为玩家还是上下家
3. 在填写好每轮玩家出牌的信息，在玩家出牌时选择AI推荐，AI即会帮助玩家推荐出牌
4. 游戏结束后弹出对话框提示输赢。


## 鸣谢
*   本项目基于[DouZero](https://github.com/kwai/DouZero)
*   灵感源自https://github.com/tianqiraf/DouZero_For_HappyDouDiZhu


