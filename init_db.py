# encoding: utf-8
import sys, os, django
from pypinyin import  Style, pinyin
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "eyes1000.settings")
django.setup()
from pet.models import *


SPECIES_LIST = (
    (1, 1, 1, '暹罗猫'),
    (2, 1, 1, '布偶猫'),
    (3, 1, 1, '苏格兰折耳猫'),
    (4, 1, 1, '英国短毛猫'),
    (5, 1, 1, '波斯猫'),
    (6, 1, 1, '俄罗斯蓝猫'),
    (7, 1, 1, '美国短毛猫'),
    (8, 1, 1, '异国短毛猫'),
    (9, 1, 1, '挪威森林猫'),
    (10, 1, 1, '孟买猫'),
    (11, 1, 1, '缅因猫'),
    (12, 1, 1, '埃及猫'),
    (13, 1, 1, '伯曼猫'),
    (14, 1, 1, '斯芬克斯猫'),
    (15, 1, 1, '缅甸猫'),
    (16, 1, 1, '阿比西尼亚猫'),
    (17, 1, 1, '新加坡猫'),
    (18, 1, 1, '索马里猫'),
    (19, 1, 1, '土耳其梵猫'),
    (20, 1, 1, '美国短尾猫'),
    (21, 1, 1, '中国狸花猫'),
    (22, 1, 1, '西伯利亚森林猫'),
    (23, 1, 1, '日本短尾猫'),
    (24, 1, 1, '巴厘猫'),
    (25, 1, 1, '土耳其安哥拉猫'),
    (26, 1, 1, '褴褛猫'),
    (27, 1, 1, '东奇尼猫'),
    (28, 1, 1, '马恩岛猫'),
    (29, 1, 1, '柯尼斯卷毛猫'),
    (30, 1, 1, '奥西猫'),
    (31, 1, 1, '沙特尔猫'),
    (32, 1, 1, '德文卷毛猫'),
    (33, 1, 1, '美国刚毛猫'),
    (34, 1, 1, '呵叻猫'),
    (35, 1, 1, '哈瓦那棕猫'),
    (36, 1, 1, '重点色短毛猫'),
    (37, 1, 1, '波米拉猫'),
    (38, 1, 1, '塞尔凯克卷毛猫'),
    (39, 1, 1, '拉邦猫'),
    (40, 1, 1, '东方猫'),
    (41, 1, 1, '美国卷毛猫'),
    (42, 1, 1, '欧洲缅甸猫'),
    (1000, 2, 1, '哈士奇'),
    (1001, 2, 1, '藏獒'),
    (1002, 2, 1, '贵宾犬'),
    (1003, 2, 1, '松狮'),
    (1004, 2, 1, '边境牧羊犬'),
    (1005, 2, 1, '吉娃娃'),
    (1006, 2, 1, '德国牧羊犬'),
    (1007, 2, 1, '秋田犬'),
    (1008, 2, 1, '蝴蝶犬'),
    (1009, 2, 1, '博美犬'),
    (1010, 2, 1, '杜宾犬'),
    (1011, 2, 1, '柴犬'),
    (1012, 2, 1, '大丹犬'),
    (1013, 2, 1, '卡斯罗'),
    (1014, 2, 1, '法国斗牛犬'),
    (1015, 2, 1, '罗威纳犬'),
    (1016, 2, 1, '英国斗牛犬'),
    (1017, 2, 1, '萨摩耶犬'),
    (1018, 2, 1, '阿富汗猎犬'),
    (1019, 2, 1, '腊肠犬'),
    (1020, 2, 1, '巴哥犬'),
    (1021, 2, 1, '西施犬'),
    (1022, 2, 1, '大白熊犬'),
    (1023, 2, 1, '圣伯纳犬'),
    (1024, 2, 1, '金毛寻回犬'),
    (1025, 2, 1, '法老王猎犬'),
    (1026, 2, 1, '斗牛梗'),
    (1027, 2, 1, '阿拉斯加雪橇犬'),
    (1028, 2, 1, '马尔济斯犬'),
    (1029, 2, 1, '兰波格犬'),
    (1030, 2, 1, '西高地白梗'),
    (1031, 2, 1, '比利时牧羊犬'),
    (1032, 2, 1, '卷毛比雄犬'),
    (1033, 2, 1, '寻血猎犬'),
    (1034, 2, 1, '纽芬兰犬'),
    (1035, 2, 1, '北京犬'),
    (1036, 2, 1, '猎兔犬'),
    (1037, 2, 1, '爱尔兰猎狼犬'),
    (1038, 2, 1, '伯恩山犬'),
    (1039, 2, 1, '喜乐蒂牧羊犬'),
    (1040, 2, 1, '波尔多犬'),
    (1041, 2, 1, '迷你杜宾'),
    (1042, 2, 1, '惠比特犬'),
    (1043, 2, 1, '中国冠毛犬'),
    (1044, 2, 1, '贝灵顿梗'),
    (1045, 2, 1, '柯利犬'),
    (1046, 2, 1, '杰克罗素梗'),
    (1047, 2, 1, '哈瓦那犬'),
    (1048, 2, 1, '苏格兰梗'),
    (1049, 2, 1, '拉布拉多寻回犬'),
    (1050, 2, 1, '大麦町犬'),
    (1051, 2, 1, '美国爱斯基摩犬'),
    (1052, 2, 1, '苏俄猎狼犬'),
    (1053, 2, 1, '万能梗'),
    (1054, 2, 1, '波音达'),
    (1055, 2, 1, '刚毛猎狐梗'),
    (1056, 2, 1, '葡萄牙水犬'),
    (1057, 2, 1, '波利犬'),
    (1058, 2, 1, '约克夏梗'),
    (1059, 2, 1, '拉萨犬'),
    (1060, 2, 1, '中国沙皮犬'),
    (1061, 2, 1, '卡迪根威尔士柯基犬'),
    (1062, 2, 1, '波士顿梗'),
    (1063, 2, 1, '比格猎犬'),
    (1064, 2, 1, '英国可卡犬'),
    (1065, 2, 1, '古代英国牧羊犬'),
    (1066, 2, 1, '小型雪纳瑞犬'),
    (1067, 2, 1, '美国可卡犬'),
    (1068, 2, 1, '巴吉度犬'),
    (1069, 2, 1, '西藏猎犬'),
    (1070, 2, 1, '马士提夫獒犬'),
    (1071, 2, 1, '斗牛獒犬'),
    (1072, 2, 1, '凯利蓝梗'),
    (1073, 2, 1, '法国狼犬'),
    (1074, 2, 1, '澳大利亚牧羊犬'),
    (1075, 2, 1, '彭布罗克威尔士柯基犬'),
    (1076, 2, 1, '英国猎狐犬'),
    (1077, 2, 1, '丝毛梗'),
    (1078, 2, 1, '匈牙利牧羊犬'),
    (1079, 2, 1, '拳狮犬'),
    (1080, 2, 1, '山地犬'),
    (1081, 2, 1, '罗得西亚脊背犬'),
    (1082, 2, 1, '西藏梗'),
    (1083, 2, 1, '湖畔梗'),
    (1084, 2, 1, '爱尔兰雪达犬'),
    (1085, 2, 1, '瑞典柯基犬'),
    (1086, 2, 1, '芬兰拉普猎犬'),
    (1087, 2, 1, '德国宾莎犬'),
    (1088, 2, 1, '库瓦兹犬'),
    (1089, 2, 1, '奇努克犬'),
    (1090, 2, 1, '巨型雪纳瑞犬'),
    (1091, 2, 1, '萨路基猎犬'),
    (1092, 2, 1, '维希拉猎犬'),
    (1093, 2, 1, '澳大利亚牧牛犬'),
    (1094, 2, 1, '威尔士梗'),
    (1095, 2, 1, '格雷伊猎犬'),
    (1096, 2, 1, '普罗特猎犬'),
    (1097, 2, 1, '墨西哥无毛犬'),
    (1098, 2, 1, '短毛猎狐梗'),
    (1099, 2, 1, '小型斗牛梗'),
    (1100, 2, 1, '斯塔福郡斗牛梗'),
    (1101, 2, 1, '威玛犬'),
    (1102, 2, 1, '意大利灰狗'),
    (1103, 2, 1, '荷兰毛狮犬'),
    (1104, 2, 1, '爱尔兰水猎犬'),
    (1105, 2, 1, '冰岛牧羊犬'),
    (1106, 2, 1, '安纳托利亚牧羊犬'),
    (1107, 2, 1, '美国猎狐犬'),
    (1108, 2, 1, '帕尔森罗塞尔梗'),
    (1109, 2, 1, '短脚长身梗'),
    (1110, 2, 1, '英国跳猎犬'),
    (1111, 2, 1, '爱尔兰梗'),
    (1112, 2, 1, '挪威伦德猎犬'),
    (1113, 2, 1, '挪威猎鹿犬'),
    (1114, 2, 1, '西帕基犬'),
    (1115, 2, 1, '波兰低地牧羊犬'),
    (1116, 2, 1, '黑俄罗斯梗'),
    (1117, 2, 1, '苏格兰猎鹿犬'),
    (1118, 2, 1, '挪威梗'),
    (1119, 2, 1, '爱尔兰红白雪达犬'),
    (1120, 2, 1, '大瑞士山地犬'),
    (1121, 2, 1, '罗秦犬'),
    (1122, 2, 1, '那不勒斯獒'),
    (1123, 2, 1, '捷克梗'),
    (1124, 2, 1, '比利时马林诺斯犬'),
    (1125, 2, 1, '标准型雪纳瑞犬'),
    (1126, 2, 1, '锡利哈姆梗'),
    (1127, 2, 1, '德国短毛波音达'),
    (1128, 2, 1, '红骨猎浣熊犬'),
    (1129, 2, 1, '巴仙吉犬'),
    (1130, 2, 1, '戈登雪达犬'),
    (1131, 2, 1, '诺福克梗'),
    (1132, 2, 1, '小型葡萄牙波登可犬'),
    (1133, 2, 1, '骑士查理王小猎犬'),
    (1134, 2, 1, '美国斯塔福郡梗'),
    (1135, 2, 1, '切萨皮克海湾寻回犬'),
    (1136, 2, 1, '粗毛柯利犬'),
    (1137, 2, 1, '玩具曼彻斯特犬'),
    (1138, 2, 1, '比利时特伏丹犬'),
    (1139, 2, 1, '玩具猎狐梗'),
    (1140, 2, 1, '日本忡'),
    (1141, 2, 1, '爱尔兰峡谷梗'),
    (1142, 2, 1, '澳大利亚梗'),
    (1143, 2, 1, '芬兰波美拉尼亚丝毛狗'),
    (1144, 2, 1, '猎水獭犬'),
    (1145, 2, 1, '挪威布哈德犬'),
    (1146, 2, 1, '爱尔兰软毛梗'),
    (1147, 2, 1, '卷毛寻回犬'),
    (1148, 2, 1, '弗莱特寻回犬'),
    (1149, 2, 1, '英国玩具犬'),
    (1150, 2, 1, '迦南犬'),
    (1151, 2, 1, '猴头梗'),
    (1152, 2, 1, '布鲁塞尔格里芬犬'),
    (1153, 2, 1, '德国硬毛波音达'),
    (1154, 2, 1, '布雷猎犬'),
    (1155, 2, 1, '黑褐猎浣熊犬'),
    (1156, 2, 1, '布列塔尼犬'),
    (1157, 2, 1, '美国水猎犬'),
    (1158, 2, 1, '西班牙小猎犬'),
    (1159, 2, 1, '树丛浣熊猎犬'),
    (1160, 2, 1, '波兰德斯布比野犬'),
    (1161, 2, 1, '比利牛斯牧羊犬'),
    (1162, 2, 1, '史毕诺犬'),
    (1163, 2, 1, '伊比赞猎犬'),
    (1164, 2, 1, '凯斯梗'),
    (1165, 2, 1, '美国英国猎浣熊犬'),
    (1166, 2, 1, '布鲁克浣熊猎犬'),
    (1167, 2, 1, '迷你贝吉格里芬凡丁犬'),
    (1168, 2, 1, '新斯科舍猎鸭寻猎犬'),
    (1169, 2, 1, '捕鼠梗'),
    (1170, 2, 1, '英格兰雪达犬'),
    (1171, 2, 1, '田野小猎犬'),
    (1172, 2, 1, '威尔士跳猎犬'),
    (1173, 2, 1, '博得猎狐犬'),
    (1174, 2, 1, '苏塞克斯猎犬'),
    (1175, 2, 1, '硬毛指示格里芬犬'),
    (1176, 2, 1, '博伊金猎犬'),
    (2000, 0, 1, '其他'),
)
def init_species():
    for species in SPECIES_LIST:
        pys = ''.join([i[0] for i in pinyin(species[3], style=Style.FIRST_LETTER)])
        pet_species = PetSpecies(id=species[0], pet_type=species[1], name=species[3], pinyin=pys)
        pet_species.save()

if __name__ == '__main__':
    init_species()
