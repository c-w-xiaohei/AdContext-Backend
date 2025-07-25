import os
import sys
from dotenv import load_dotenv

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# 加载环境变量
load_dotenv()
print('环境变量已加载')

api_key = os.getenv('MEM0_API_KEY')
print(f'MEM0_API_KEY: {api_key[:10] if api_key else "未设置"}...')

# 导入模块
from schemas.privacy import PrivacyLevel  
from schemas.common import Metadata
from storage.service import StorageService

def test_storage_service():
    """测试存储服务功能"""
    service = StorageService()
    print('StorageService实例已创建，可以开始测试')
    
    # 创建正确的元数据对象
    metadata = Metadata(
        privacy_level=PrivacyLevel.LEVEL_1_PUBLIC,  # 修正枚举值
        source="user"
    )
    tishici="""
    AdventureX 2025 终极指南
English Version | 中文版

我们非常期待能在 AdventureX 2025 与超酷的你相见，这是一份终极指南，里面包含了所有你需要了解的内容，如果我们漏掉了一些内容，或者你在看完文档后依然有问题，欢迎与我们联系：support@adventure-x.org，或者在 AdventureX 2025 总群中与我们联系，我们将会尽我们的全力帮助你～（由于人数众多，若有消息遗漏请通过邮件联系）

🟢 本文档绝大部分内容同时也适用于：游客、合作方、指引者

📍 时间和地点
AdventureX 2025 将于 2025 年 7 月 23 日至 27 日在 杭州湖畔创研中心 以及 杭州未来科技城学术交流中心 举行，分别位于中国浙江省杭州市余杭区礼贤路 9 号和中国浙江省杭州市余杭区仓前街道良睦路 1399 号。
签到会在湖畔创研中心和学术交流中心分别举行。我们建议你率先前往学术交流中心签名与逛展，然后前往湖畔创研中心签到，并领取对应的选手物料（建议在 23 日晚 7:30 前完成）。我们几乎所有的 Hacking 和活动都在湖畔创研中心举行。开幕式、闭幕式、Super！展会、选手项目 Expo、音乐节将在学术交流中心举行。

📦 行囊单
1. 身份证 / 护照（需要实体身份证）
2. 学生证或任何证明你学生身份的文件（如果你的年龄超过 26 岁）
  - 如果你没有申请出行/住宿补贴或年龄小于等于 26 岁，则不需要提供
3. 你的 AdventureX 通行二维码（可以在 united.adventure-x.org 找到，现场也会分发挂牌，请一直佩戴，否则会被保安请出场地）（二维码有时效，请不要截图，也不要分享给他人）
4. 智能设备，电脑和配件（鼠标、键盘等）
5. 充电器（包含电话、笔记本电脑等）
6. 你可能想用于 Hack 的任何硬件。
  - 我们会提供部分，但是如果你有特别酷的设备，欢迎携带
7. 与睡眠有关的东西（睡袋、枕头、毯子等）
  - 我们会提供一定数量的睡袋（会循环使用），所以如果有洁癖的同学可以自带睡袋～
  - 蓝盒子将会提供一些改良版本的蓝垫子（会循环使用）
  - 非常推荐自带毯子，晚上场馆比较冷
8. 换洗衣物
9. 洗漱用品，牙刷/牙膏，淋浴用品
10. 耳机/耳塞
11. 药物，如果需要的话
12. 雨伞、雨衣等任何防止你被淋湿的东西
13. 水杯，食物（我们提供，如果你想带其他的也没有问题）

⏰ 时间安排 
下面是我们目前对于 AdventureX 2025 的关键时间安排，我们准备了各种活动和精彩的 @Workshop，以及与一些特邀嘉宾带来难以置信的演讲：

7 月 23 日
- 10:00am-11:30pm：签到
  - 前往签名墙合影留念（学术交流中心）
  - 签到并领取 AdventureX 选手专属礼包（在湖畔创研中心）（必须在 7 月 23 日当天签到，否则席位将被取消）
    - 如果你因不可抗力无法在 23 日前往会场，你可以联系@巫昊林 申请延期一天（24 日下午 3 点前必须到场），请说明理由并出示证明（上班、旅游等不属于可以接受的理由）
  - 参与合作伙伴 SUPER！展览（学术交流中心）（快来领取超酷的贴纸和伴手礼，以及参与有趣的小活动）
    - 23 日展会结束时间：下午 5 点（下午 4 点禁止入内）
    - 🟢 本活动对外开放，无须通行二维码，可以直接入内
  - 如果你是选手，请确保你在 23 日前在 United Portal 中完成 ULTIMATE TEST，否则你将无法进入湖畔创研中心。
- 6:40pm-9:30pm：开幕式（学术交流中心）（6:10 分可以入场）
  - 观看 AdventureX 2025 主题 Keynote（是的，我们学习了下苹果 😝）
    - 主旨演讲
    - 场地介绍
    - 赛道与规则
  - Talkshow 嘉宾演讲
  - 📝 备注：你需要完整的参与开幕式，开幕式期间湖畔创研中心不开放（直到开幕式结束）
  - 🟢 本活动对外开放，无须通行二维码，可以直接入内

7 月 24 日至 7 月 26 日
- 7 月 24 日 1:00am：硬件实验室开放（端点 G）
- 10:00am - 8:30pm: Super! 展会（学术交流中心）
- 全天 24H：Hacking - 写代码时间（湖畔创研中心）
- 早上或下午：@Workshop（湖畔创研中心）
- 傍晚与凌晨：蓝调活动（湖畔创研中心）

7 月 27 日
- 7:00am：项目提交通道关闭
- 9:00am-3:00pm：选手项目 Expo（学术交流中心）
  - 在 3:30 之前需要将所有东西清理场地，同时你需要将自己的桌子搬出去到户外的过道上
  - 没有搬的会减 3 积分
  - 🟢 本活动对外开放，无须通行二维码，可以直接入内
- 4:30pm-5:45pm：闭幕式（学术交流中心）
  - 🟢 本活动对外开放，无须通行二维码，可以直接入内
- 6:30pm-10:30pm：“伍德斯托克”音乐节（学术交流中心）
  - 🟢 本活动对外开放，无须通行二维码，可以直接入内
- 11:30pm：场馆关闭（学术交流中心&湖畔创研中心）

✨ Talkshow 嘉宾演讲
[图片]
[图片]
[图片]
[图片]
[图片]
[图片]
[图片]
[图片]
[图片]
[图片]
[图片]
[图片]

😎 Super! 展会
Super! 展会是 AdventureX 推出的超大型摆摊活动。超过 100+ 科技企业与社区将会来到活动现场，你可以在这里与喜欢的公司面对面交流，领取周边，体验各种新玩意！还有各种神秘玩法等你解锁～

- 时间：7 月 23 日 - 7 月 26 日
  - 每天早上 10 点开放
  - 23 日结束时间为晚上 6 点，其他时间均为晚上 8:30
- 地点：学术交流中心
- 🟢 本活动对外开放，无须通行二维码，可以直接入内
- 📝 备注：在 4 天内打卡 100 个展位，就可以获得 6 点积分欧
    """
    # 添加测试上下文
    result1 = service.add(text=tishici, metadata=metadata)
    print(f"添加结果1: {result1}")

    # result2 = service.add("项目使用Python和FastAPI框架开发", metadata=metadata)
    # print(f"添加结果2: {result2}")

    # result3 = service.add("用户偏好深色主题界面", metadata=metadata)
    # print(f"添加结果3: {result3}")

    # 测试搜索功能
    print("\n=== 搜索测试 ===")
    search_results = service.search("咖啡")
    print(f"搜索'咖啡'的结果: {len(search_results)} 条")
    for i, result in enumerate(search_results):
        print(f"  {i+1}. {result}")

    # 测试列表功能
    print("\n=== 列表测试 ===")
    all_memories = service.list(limit=10)
    print(f"所有记忆: {len(all_memories)} 条")
    for i, memory in enumerate(all_memories):
        print(f"  {i+1}. {memory}")

    #测试删除功能
    print("\n测试删除功能")
    delete_result = service.delete(all_memories[0]['id'])
    print(f"删除结果: {delete_result}")


if __name__ == "__main__":
    test_storage_service()