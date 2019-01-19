CREATE DATABASE IF NOT EXISTS naiba_eyes default character set utf8 COLLATE utf8_general_ci;

DROP TABLE IF EXISTS `t_pet_lost`;
CREATE TABLE `t_pet_lost` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `flag` tinyint(4) NOT NULL COMMENT '1：有效，2：无效',
  `publisher_id` int(11) NOT NULL COMMENT '发布者id',
  `material_ids` varchar(1000) DEFAULT NULL COMMENT '素材id',
  `species_id` int(11) NOT NULL COMMENT '物种',
  `class_id` int(11) DEFAULT NULL COMMENT '种类',
  `gender` tinyint DEFAULT NULL COMMENT '0:MALE, 1:FEMALE, 2:UNKNOWN',
  `color` varchar(20) DEFAULT NULL COMMENT '颜色',
  `description` text DEFAULT NULL COMMENT '描述',
  `region_id` int(11) NOT NULL COMMENT '地区',
  `place` varchar(100) DEFAULT NULL COMMENT '地点',
  `longitude` float DEFAULT NULL COMMENT '经度',
  `latitude` float DEFAULT NULL COMMENT '维度',
  `status` tinyint(4) NOT NULL COMMENT '0:发布中，1：结案，2：过期',
  `audit_status` tinyint(4) NOT NULL COMMENT '0：待审核，1：审核通过，2：审核拒绝',
  `is_in_boost` boolean DEFAULT NULL,
  `boost_kpi_type` tinyint(4) DEFAULT NULL COMMENT '助力种类。0:浏览量',
  `boost_amount` int(11) NOT NULL COMMENT '助力金额',
  `boost_scope` int(11) NOT NULL COMMENT '范围(米)',
  `boost_count` int(11) DEFAULT NULL COMMENT '助力数',
  `publish_charge_status` tinyint(4) DEFAULT NULL COMMENT '发布扣费状态。0:代付款，1：付款失败，2：付款成功，3：免费',
  `publish_charge_amount` int(11) NOT NULL DEFAULT '0' COMMENT '发布扣费金额，单位分',
  `boost_charge_status` tinyint(4) DEFAULT NULL COMMENT '助力扣费状态。0:代付款，1：付款失败，2：付款成功，3：免费',
  `boost_charge_amount` int(11) NOT NULL DEFAULT '0' COMMENT '助力扣费金额，单位分',
  `browse_count` int(11) NOT NULL DEFAULT '0' COMMENT '浏览数量',
  `forward_count` int(11) NOT NULL DEFAULT '0' COMMENT '转发数量',
  `praise_count` int(11) NOT NULL DEFAULT '0' COMMENT '点赞数量',
  `medical_treatment_status` int(11) NOT NULL DEFAULT '0' COMMENT '0x01：已绝育，0x02：已免疫，0x04：已驱虫',
  `create_by` int(11) NOT NULL,
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `last_update_by` int(11) NOT NULL,
  `last_update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `t_contact_relation`;
CREATE TABLE `t_contact_relation` (
  `id_a` int(11) NOT NULL,
  `id_b` int(11) NOT NULL,
  `flag` tinyint(4) NOT NULL COMMENT '1：有效，2：无效',
  `first_ref_type` tinyint(4) NOT NULL COMMENT '0：走失发布，1：线索发布',
  `first_ref_id` int(11) NOT NULL COMMENT '走失发布or线索id',
  `create_by` int(11) NOT NULL,
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `last_update_by` int(11) NOT NULL,
  `last_update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_a`,`id_b`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT '私信联系人';

DROP TABLE IF EXISTS `t_private_contact`;
CREATE TABLE `t_private_contact` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `flag` tinyint(4) NOT NULL COMMENT '1：有效，2：无效',
  `id_src` int(11) NOT NULL,
  `id_dst` int(11) NOT NULL,
  `message` text NOT NULL,
  `create_by` int(11) NOT NULL,
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `last_update_by` int(11) NOT NULL,
  `last_update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT '私信';

DROP TABLE IF EXISTS `t_pet_lost_found_tag`;
CREATE TABLE `t_pet_lost_found_tag` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `flag` tinyint(4) NOT NULL COMMENT '1：有效，2：无效',
  `ref_type` tinyint(4) NOT NULL COMMENT '0：走失发布，1：线索发布',
  `ref_id` int(11) NOT NULL COMMENT '走失发布or线索id',
  `tag_id` bigint(20) NOT NULL,
  `create_by` int(11) NOT NULL,
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `last_update_by` int(11) NOT NULL,
  `last_update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT '宠物关联描述tag';

DROP TABLE IF EXISTS `t_pet_lost_found_comment`;
CREATE TABLE `t_pet_lost_found_comment` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `flag` tinyint(4) NOT NULL COMMENT '1：有效，2：无效',
  `publisher_id` int(11) NOT NULL COMMENT '发布者id',
  `ref_type` tinyint(4) NOT NULL COMMENT '0：走失发布，1：线索发布',
  `ref_id` int(11) NOT NULL COMMENT '走失发布or线索id',
  `tag_id` bigint(20) NOT NULL,
  `audit_status` tinyint(4) NOT NULL DEFAULT '1' COMMENT '0：待审核，1：审核通过，2：审核拒绝',
  `create_by` int(11) NOT NULL,
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `last_update_by` int(11) NOT NULL,
  `last_update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT '宠物发布comment';

DROP TABLE IF EXISTS `t_pet_lost_boost`;
CREATE TABLE `t_pet_lost_boost` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `flag` tinyint(4) NOT NULL COMMENT '1：有效，2：无效',
  `publisher_id` int(11) NOT NULL COMMENT '发布者id',
  `lost_id` int(11) NOT NULL COMMENT '走失发布id',
  `booster_id` int(11) NOT NULL,
  `booster_nickname` varchar(50) NOT NULL,
  `boost_count` int(11) NOT NULL COMMENT '助力次数',
  `create_by` int(11) NOT NULL,
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `last_update_by` int(11) NOT NULL,
  `last_update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT '走失寻找助力';

DROP TABLE IF EXISTS `t_pet_tag`;
CREATE TABLE `t_pet_tag` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `flag` tinyint(4) NOT NULL COMMENT '1：有效，2：无效',
  `publisher_id` int(11) NOT NULL COMMENT '发布者id',
  `name` varchar(10) NOT NULL COMMENT 'tag名',
  `frequency` double DEFAULT '0',
  `score` double DEFAULT '0',
  `create_by` int(11) NOT NULL,
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `last_update_by` int(11) NOT NULL,
  `last_update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT '宠物描述tag';

DROP TABLE IF EXISTS `t_pet_found`;
CREATE TABLE `t_pet_found` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `flag` tinyint(4) NOT NULL COMMENT '1：有效，2：无效',
  `publisher_id` int(11) NOT NULL COMMENT '发布者id',
  `lost_ref_id` int(11) DEFAULT NULL COMMENT '关联走失发布id',
  `material_ids` varchar(1000) DEFAULT NULL COMMENT '素材id',
  `species_id` int(11) NOT NULL COMMENT '物种',
  `class_id` int(11) DEFAULT NULL COMMENT '种类',
  `color` varchar(20) DEFAULT NULL COMMENT '颜色',
  `description` text DEFAULT NULL COMMENT '描述',
  `region_id` int(11) NOT NULL COMMENT '地区',
  `place` varchar(100) DEFAULT NULL COMMENT '地点',
  `found_status` tinyint(4) NOT NULL DEFAULT '0' COMMENT '0:宠物不在身边，1：宠物在身边，2：宠物在医院',
  `status` tinyint(4) NOT NULL COMMENT '0:发布中，2：过期',
  `audit_status` tinyint(4) NOT NULL COMMENT '0：待审核，1：审核通过，2：审核拒绝',
  `browse_count` int(11) NOT NULL DEFAULT '0' COMMENT '浏览数量',
  `forward_count` int(11) NOT NULL DEFAULT '0' COMMENT '转发数量',
  `praise_count` int(11) NOT NULL DEFAULT '0' COMMENT '点赞数量',
  `create_by` int(11) NOT NULL,
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `last_update_by` int(11) NOT NULL,
  `last_update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `t_pet_lost_found`;
CREATE TABLE `t_pet_lost_found` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `flag` tinyint(4) NOT NULL COMMENT '1：有效，2：无效',
  `lost_id` int(11) NOT NULL COMMENT '走失发布id',
  `found_id` int(11) DEFAULT NULL COMMENT '线索发布id',
  `publisher_id` int(11) NOT NULL COMMENT '发布者id',
  `static_score` float DEFAULT NULL COMMENT '静态评分',
  `feedback_score` float DEFAULT NULL COMMENT '失主评分',
  `contact_status` tinyint(4) NOT NULL COMMENT '0:失主未联系，1：失主已联系',
  `create_by` int(11) NOT NULL,
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `last_update_by` int(11) NOT NULL,
  `last_update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `t_pet_lost_found_close`;
CREATE TABLE `t_pet_lost_found_close` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `flag` tinyint(4) NOT NULL COMMENT '1：有效，2：无效',
  `lost_id` int(11) NOT NULL COMMENT '走失发布id',
  `best_found_id` int(11) NOT NULL COMMENT '线索发布id',
  `description` text DEFAULT NULL COMMENT '描述',
  `material_ids` varchar(1000) DEFAULT NULL COMMENT '素材id',
  `browse_count` int(11) NOT NULL DEFAULT '0' COMMENT '浏览数量',
  `forward_count` int(11) NOT NULL DEFAULT '0' COMMENT '转发数量',
  `praise_count` int(11) NOT NULL DEFAULT '0' COMMENT '点赞数量',
  `reward_charge_status` tinyint(4) DEFAULT NULL COMMENT '打赏扣费状态。0:代付款，1：付款失败，2：付款成功，3：免费',
  `reward_charge_amount` int(11) NOT NULL DEFAULT '0' COMMENT '打赏扣费金额，单位分',
  `create_by` int(11) NOT NULL,
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `last_update_by` int(11) NOT NULL,
  `last_update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `t_pet_material`;
CREATE TABLE `t_pet_material` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `flag` tinyint(4) NOT NULL COMMENT '1：有效，2：无效',
  `publisher_id` int(11) NOT NULL COMMENT '发布者id',
  `material_type` tinyint(11) NOT NULL COMMENT '0：视频，1：图片',
  `description` text DEFAULT NULL COMMENT '描述',
  `mime_type` varchar(20) DEFAULT NULL,
  `size` int(11) NOT NULL,
  `md5` varchar(100) NOT NULL,
  `url` varchar(1000) NOT NULL,
  `create_by` int(11) NOT NULL,
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `last_update_by` int(11) NOT NULL,
  `last_update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `t_user`;
CREATE TABLE `t_user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `flag` tinyint(4) NOT NULL COMMENT '1：有效，2：无效',
  `wechat_appid` varchar(100) NOT NULL COMMENT '公众号appid',
  `openid` varchar(100) NOT NULL COMMENT '公众号openid',
  `unionid` varchar(100) DEFAULT NULL,
  `wechat_nick_name` varchar(50) DEFAULT NULL COMMENT '微信呢称',
  `wechat_gender` tinyint DEFAULT NULL COMMENT '0:MALE, 1:FEMALE',
  `gender` tinyint DEFAULT NULL COMMENT '0:MALE, 1:FEMALE',
  `region_id` int(11) DEFAULT NULL COMMENT '地区',
  `wechat_country` varchar(20) DEFAULT NULL COMMENT 'from wechat',
  `wechat_province` varchar(20) DEFAULT NULL COMMENT 'from wechat',
  `wechat_city` varchar(20) DEFAULT NULL COMMENT 'from wechat',
  `wechat_avatar_url` varchar(1000) DEFAULT NULL COMMENT 'from wechat',
  `phone` varchar(20) DEFAULT NULL,
  `birthday` date DEFAULT NULL,
  `address` varchar(100) DEFAULT NULL,
  `member_score` int(11) NOT NULL DEFAULT '0',
  `member_level` int(11) NOT NULL DEFAULT '0',
  `welfare_amount` int(11) NOT NULL DEFAULT '0',
  `credit_score` int(11) NOT NULL DEFAULT '100',
  `role_id` int(11) NOT NULL DEFAULT '3',
  `create_by` int(11) NOT NULL,
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `last_update_by` int(11) NOT NULL,
  `last_update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `t_user`;
CREATE TABLE `t_user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `flag` tinyint(4) NOT NULL COMMENT '1：有效，2：无效',
  `wechat_appid` varchar(100) NOT NULL COMMENT '公众号appid',
  `openid` varchar(100) NOT NULL COMMENT '公众号openid',
  `unionid` varchar(100) DEFAULT NULL,
  `wechat_nick_name` varchar(50) DEFAULT NULL COMMENT '微信呢称',
  `wechat_gender` tinyint DEFAULT NULL COMMENT '0:MALE, 1:FEMALE',
  `gender` tinyint DEFAULT NULL COMMENT '0:MALE, 1:FEMALE',
  `region_id` int(11) DEFAULT NULL COMMENT '地区',
  `wechat_country` varchar(20) DEFAULT NULL COMMENT 'from wechat',
  `wechat_province` varchar(20) DEFAULT NULL COMMENT 'from wechat',
  `wechat_city` varchar(20) DEFAULT NULL COMMENT 'from wechat',
  `wechat_avatar_url` varchar(1000) DEFAULT NULL COMMENT 'from wechat',
  `phone` varchar(20) DEFAULT NULL,
  `birthday` date DEFAULT NULL,
  `address` varchar(100) DEFAULT NULL,
  `member_score` int(11) NOT NULL DEFAULT '0',
  `member_level` int(11) NOT NULL DEFAULT '0',
  `welfare_amount` int(11) NOT NULL DEFAULT '0',
  `credit_score` int(11) NOT NULL DEFAULT '100',
  `role_id` int(11) NOT NULL DEFAULT '3',
  `create_by` int(11) NOT NULL,
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `last_update_by` int(11) NOT NULL,
  `last_update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `t_user_account`;
CREATE TABLE `t_user_account` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `flag` tinyint(4) NOT NULL COMMENT '1：有效，2：无效',
  `user_id` int(11) NOT NULL,
  `account_type` tinyint(4) NOT NULL COMMENT '0:公益金，1:积分，2:信用分',
  `action_type` tinyint(4) NOT NULL COMMENT '0:助力，1:发布线索，2:结案',
  `op_type` tinyint(4) NOT NULL COMMENT '0:增加，1:减少',
  `amount` int(11) NOT NULL,
  `create_by` int(11) NOT NULL,
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `last_update_by` int(11) NOT NULL,
  `last_update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `t_product`;
CREATE TABLE `t_product` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `flag` tinyint(4) NOT NULL COMMENT '1：有效，2：无效',
  `name` varchar(20) NOT NULL COMMENT '名称',
  `description` text DEFAULT NULL COMMENT '描述',
  `price` int(11) NOT NULL,
  `create_by` int(11) NOT NULL,
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `last_update_by` int(11) NOT NULL,
  `last_update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `t_order`;
CREATE TABLE `t_order` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `flag` tinyint(4) NOT NULL COMMENT '1：有效，2：无效',
  `user_id` int(11) NOT NULL,
  `pay_type` tinyint(4) NOT NULL COMMENT '支付方式，0：微信零钱，1：微信银行借记卡，2：微信银行信用卡',
  `appid` varchar(100) NOT NULL COMMENT '微信支付分配的公众账号ID',
  `mch_id` varchar(100) NOT NULL COMMENT '微信支付分配的商户号',
  `goods_description` text DEFAULT NULL COMMENT '描述',
  `fee_type` varchar(5) NOT NULL DEFAULT 'CNY' COMMENT '符合ISO4217标准的三位字母代码',
  `total_fee` int(11) NOT NULL,
  `product_id` int(11) NOT NULL,
  `product_amount` int(11) NOT NULL,
  `pet_lost_id` int(11) DEFAULT NULL COMMENT '走失发布id',
  `status` tinyint(4) NOT NULL COMMENT '0: 未支付,1:支付成功，2：支付错误，3：关单，4：退款',
  `refund_status` tinyint(4) NOT NULL COMMENT '0:待审核，1：审核通过，2：审核拒绝, 3：退款中，4：退款成功，5：退款失败',
  `create_by` int(11) NOT NULL,
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `last_update_by` int(11) NOT NULL,
  `last_update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `t_pet_lost_interact_hourly`;
CREATE TABLE `t_pet_lost_interact_hourly` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `flag` tinyint(4) NOT NULL COMMENT '1：有效，2：无效',
  `date_id` int(8) NOT NULL,
  `hour_id` tinyint(2) NOT NULL,
  `share_num` int(11) NOT NULL DEFAULT '0',
  `pv` int(11) NOT NULL DEFAULT '0',
  `uv` int(11) NOT NULL DEFAULT '0',
  `valid_uv` int(11) NOT NULL DEFAULT '0',
  `boost_uv` int(11) NOT NULL DEFAULT '0',
  `praise_count` int(11) NOT NULL DEFAULT '0',
  `charge` int(11) NOT NULL DEFAULT '0',
  `create_by` int(11) NOT NULL,
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `last_update_by` int(11) NOT NULL,
  `last_update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `t_pet_found_interact_hourly`;
CREATE TABLE `t_pet_found_interact_hourly` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `flag` tinyint(4) NOT NULL COMMENT '1：有效，2：无效',
  `date_id` int(8) NOT NULL,
  `hour_id` tinyint(2) NOT NULL,
  `share_num` int(11) NOT NULL DEFAULT '0',
  `pv` int(11) NOT NULL DEFAULT '0',
  `uv` int(11) NOT NULL DEFAULT '0',
  `praise_count` int(11) NOT NULL DEFAULT '0',
  `create_by` int(11) NOT NULL,
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `last_update_by` int(11) NOT NULL,
  `last_update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `t_dt_role`;
CREATE TABLE `t_dt_role` (
  `id` smallint NOT NULL AUTO_INCREMENT,
  `flag` tinyint(4) NOT NULL COMMENT '1：有效，2：无效',
  `name` varchar(20) NOT NULL COMMENT '名称',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO `t_dt_role` VALUES (1, 1, '管理员');
INSERT INTO `t_dt_role` VALUES (2, 1, '运营');
INSERT INTO `t_dt_role` VALUES (3, 1, '用户');

DROP TABLE IF EXISTS `t_dt_pet_species`;
CREATE TABLE `t_dt_pet_species` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `flag` tinyint(4) NOT NULL COMMENT '1：有效，2：无效',
  `name` varchar(20) NOT NULL COMMENT '名称',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO `t_dt_pet_species` VALUES (1, 1, '猫');
INSERT INTO `t_dt_pet_species` VALUES (2, 1, '狗');

DROP TABLE IF EXISTS `t_dt_pet_class`;
CREATE TABLE `t_dt_pet_class` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `flag` tinyint(4) NOT NULL COMMENT '1：有效，2：无效',
  `species_id` int(11) NOT NULL COMMENT '物种id',
  `name` varchar(20) NOT NULL COMMENT '名称',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
INSERT INTO `t_dt_pet_class` VALUES (1, 1, 1, '暹罗猫');
INSERT INTO `t_dt_pet_class` VALUES (2, 1, 1, '布偶猫');
INSERT INTO `t_dt_pet_class` VALUES (3, 1, 1, '苏格兰折耳猫');
INSERT INTO `t_dt_pet_class` VALUES (4, 1, 1, '英国短毛猫');
INSERT INTO `t_dt_pet_class` VALUES (5, 1, 1, '波斯猫');
INSERT INTO `t_dt_pet_class` VALUES (6, 1, 1, '俄罗斯蓝猫');
INSERT INTO `t_dt_pet_class` VALUES (7, 1, 1, '美国短毛猫');
INSERT INTO `t_dt_pet_class` VALUES (8, 1, 1, '异国短毛猫');
INSERT INTO `t_dt_pet_class` VALUES (9, 1, 1, '挪威森林猫');
INSERT INTO `t_dt_pet_class` VALUES (10, 1, 1, '孟买猫');
INSERT INTO `t_dt_pet_class` VALUES (11, 1, 1, '缅因猫');
INSERT INTO `t_dt_pet_class` VALUES (12, 1, 1, '埃及猫');
INSERT INTO `t_dt_pet_class` VALUES (13, 1, 1, '伯曼猫');
INSERT INTO `t_dt_pet_class` VALUES (14, 1, 1, '斯芬克斯猫');
INSERT INTO `t_dt_pet_class` VALUES (15, 1, 1, '缅甸猫');
INSERT INTO `t_dt_pet_class` VALUES (16, 1, 1, '阿比西尼亚猫');
INSERT INTO `t_dt_pet_class` VALUES (17, 1, 1, '新加坡猫');
INSERT INTO `t_dt_pet_class` VALUES (18, 1, 1, '索马里猫');
INSERT INTO `t_dt_pet_class` VALUES (19, 1, 1, '土耳其梵猫');
INSERT INTO `t_dt_pet_class` VALUES (20, 1, 1, '美国短尾猫');
INSERT INTO `t_dt_pet_class` VALUES (21, 1, 1, '中国狸花猫');
INSERT INTO `t_dt_pet_class` VALUES (22, 1, 1, '西伯利亚森林猫');
INSERT INTO `t_dt_pet_class` VALUES (23, 1, 1, '日本短尾猫');
INSERT INTO `t_dt_pet_class` VALUES (24, 1, 1, '巴厘猫');
INSERT INTO `t_dt_pet_class` VALUES (25, 1, 1, '土耳其安哥拉猫');
INSERT INTO `t_dt_pet_class` VALUES (26, 1, 1, '褴褛猫');
INSERT INTO `t_dt_pet_class` VALUES (27, 1, 1, '东奇尼猫');
INSERT INTO `t_dt_pet_class` VALUES (28, 1, 1, '马恩岛猫');
INSERT INTO `t_dt_pet_class` VALUES (29, 1, 1, '柯尼斯卷毛猫');
INSERT INTO `t_dt_pet_class` VALUES (30, 1, 1, '奥西猫');
INSERT INTO `t_dt_pet_class` VALUES (31, 1, 1, '沙特尔猫');
INSERT INTO `t_dt_pet_class` VALUES (32, 1, 1, '德文卷毛猫');
INSERT INTO `t_dt_pet_class` VALUES (33, 1, 1, '美国刚毛猫');
INSERT INTO `t_dt_pet_class` VALUES (34, 1, 1, '呵叻猫');
INSERT INTO `t_dt_pet_class` VALUES (35, 1, 1, '哈瓦那棕猫');
INSERT INTO `t_dt_pet_class` VALUES (36, 1, 1, '重点色短毛猫');
INSERT INTO `t_dt_pet_class` VALUES (37, 1, 1, '波米拉猫');
INSERT INTO `t_dt_pet_class` VALUES (38, 1, 1, '塞尔凯克卷毛猫');
INSERT INTO `t_dt_pet_class` VALUES (39, 1, 1, '拉邦猫');
INSERT INTO `t_dt_pet_class` VALUES (40, 1, 1, '东方猫');
INSERT INTO `t_dt_pet_class` VALUES (41, 1, 1, '美国卷毛猫');
INSERT INTO `t_dt_pet_class` VALUES (42, 1, 1, '欧洲缅甸猫');


INSERT INTO `t_dt_pet_class` VALUES (1000, 2, 1, '哈士奇');
INSERT INTO `t_dt_pet_class` VALUES (1001, 2, 1, '藏獒');
INSERT INTO `t_dt_pet_class` VALUES (1002, 2, 1, '贵宾犬');
INSERT INTO `t_dt_pet_class` VALUES (1003, 2, 1, '松狮');
INSERT INTO `t_dt_pet_class` VALUES (1004, 2, 1, '边境牧羊犬');
INSERT INTO `t_dt_pet_class` VALUES (1005, 2, 1, '吉娃娃');
INSERT INTO `t_dt_pet_class` VALUES (1006, 2, 1, '德国牧羊犬');
INSERT INTO `t_dt_pet_class` VALUES (1007, 2, 1, '秋田犬');
INSERT INTO `t_dt_pet_class` VALUES (1008, 2, 1, '蝴蝶犬');
INSERT INTO `t_dt_pet_class` VALUES (1009, 2, 1, '博美犬');
INSERT INTO `t_dt_pet_class` VALUES (1010, 2, 1, '杜宾犬');
INSERT INTO `t_dt_pet_class` VALUES (1011, 2, 1, '柴犬');
INSERT INTO `t_dt_pet_class` VALUES (1012, 2, 1, '大丹犬');
INSERT INTO `t_dt_pet_class` VALUES (1013, 2, 1, '卡斯罗');
INSERT INTO `t_dt_pet_class` VALUES (1014, 2, 1, '法国斗牛犬');
INSERT INTO `t_dt_pet_class` VALUES (1015, 2, 1, '罗威纳犬');
INSERT INTO `t_dt_pet_class` VALUES (1016, 2, 1, '英国斗牛犬');
INSERT INTO `t_dt_pet_class` VALUES (1017, 2, 1, '萨摩耶犬');
INSERT INTO `t_dt_pet_class` VALUES (1018, 2, 1, '阿富汗猎犬');
INSERT INTO `t_dt_pet_class` VALUES (1019, 2, 1, '腊肠犬');
INSERT INTO `t_dt_pet_class` VALUES (1020, 2, 1, '巴哥犬');
INSERT INTO `t_dt_pet_class` VALUES (1021, 2, 1, '西施犬');
INSERT INTO `t_dt_pet_class` VALUES (1022, 2, 1, '大白熊犬');
INSERT INTO `t_dt_pet_class` VALUES (1023, 2, 1, '圣伯纳犬');
INSERT INTO `t_dt_pet_class` VALUES (1024, 2, 1, '金毛寻回犬');
INSERT INTO `t_dt_pet_class` VALUES (1025, 2, 1, '法老王猎犬');
INSERT INTO `t_dt_pet_class` VALUES (1026, 2, 1, '斗牛梗');
INSERT INTO `t_dt_pet_class` VALUES (1027, 2, 1, '阿拉斯加雪橇犬');
INSERT INTO `t_dt_pet_class` VALUES (1028, 2, 1, '马尔济斯犬');
INSERT INTO `t_dt_pet_class` VALUES (1029, 2, 1, '兰波格犬');
INSERT INTO `t_dt_pet_class` VALUES (1030, 2, 1, '西高地白梗');
INSERT INTO `t_dt_pet_class` VALUES (1031, 2, 1, '比利时牧羊犬');
INSERT INTO `t_dt_pet_class` VALUES (1032, 2, 1, '卷毛比雄犬');
INSERT INTO `t_dt_pet_class` VALUES (1033, 2, 1, '寻血猎犬');
INSERT INTO `t_dt_pet_class` VALUES (1034, 2, 1, '纽芬兰犬');
INSERT INTO `t_dt_pet_class` VALUES (1035, 2, 1, '北京犬');
INSERT INTO `t_dt_pet_class` VALUES (1036, 2, 1, '猎兔犬');
INSERT INTO `t_dt_pet_class` VALUES (1037, 2, 1, '爱尔兰猎狼犬');
INSERT INTO `t_dt_pet_class` VALUES (1038, 2, 1, '伯恩山犬');
INSERT INTO `t_dt_pet_class` VALUES (1039, 2, 1, '喜乐蒂牧羊犬');
INSERT INTO `t_dt_pet_class` VALUES (1040, 2, 1, '波尔多犬');
INSERT INTO `t_dt_pet_class` VALUES (1041, 2, 1, '迷你杜宾');
INSERT INTO `t_dt_pet_class` VALUES (1042, 2, 1, '惠比特犬');
INSERT INTO `t_dt_pet_class` VALUES (1043, 2, 1, '中国冠毛犬');
INSERT INTO `t_dt_pet_class` VALUES (1044, 2, 1, '贝灵顿梗');
INSERT INTO `t_dt_pet_class` VALUES (1045, 2, 1, '柯利犬');
INSERT INTO `t_dt_pet_class` VALUES (1046, 2, 1, '杰克罗素梗');
INSERT INTO `t_dt_pet_class` VALUES (1047, 2, 1, '哈瓦那犬');
INSERT INTO `t_dt_pet_class` VALUES (1048, 2, 1, '苏格兰梗');
INSERT INTO `t_dt_pet_class` VALUES (1049, 2, 1, '拉布拉多寻回犬');
INSERT INTO `t_dt_pet_class` VALUES (1050, 2, 1, '大麦町犬');
INSERT INTO `t_dt_pet_class` VALUES (1051, 2, 1, '美国爱斯基摩犬');
INSERT INTO `t_dt_pet_class` VALUES (1052, 2, 1, '苏俄猎狼犬');
INSERT INTO `t_dt_pet_class` VALUES (1053, 2, 1, '万能梗');
INSERT INTO `t_dt_pet_class` VALUES (1054, 2, 1, '波音达');
INSERT INTO `t_dt_pet_class` VALUES (1055, 2, 1, '刚毛猎狐梗');
INSERT INTO `t_dt_pet_class` VALUES (1056, 2, 1, '葡萄牙水犬');
INSERT INTO `t_dt_pet_class` VALUES (1057, 2, 1, '波利犬');
INSERT INTO `t_dt_pet_class` VALUES (1058, 2, 1, '约克夏梗');
INSERT INTO `t_dt_pet_class` VALUES (1059, 2, 1, '拉萨犬');
INSERT INTO `t_dt_pet_class` VALUES (1060, 2, 1, '中国沙皮犬');
INSERT INTO `t_dt_pet_class` VALUES (1061, 2, 1, '卡迪根威尔士柯基犬');
INSERT INTO `t_dt_pet_class` VALUES (1062, 2, 1, '波士顿梗');
INSERT INTO `t_dt_pet_class` VALUES (1063, 2, 1, '比格猎犬');
INSERT INTO `t_dt_pet_class` VALUES (1064, 2, 1, '英国可卡犬');
INSERT INTO `t_dt_pet_class` VALUES (1065, 2, 1, '古代英国牧羊犬');
INSERT INTO `t_dt_pet_class` VALUES (1066, 2, 1, '小型雪纳瑞犬');
INSERT INTO `t_dt_pet_class` VALUES (1067, 2, 1, '美国可卡犬');
INSERT INTO `t_dt_pet_class` VALUES (1068, 2, 1, '巴吉度犬');
INSERT INTO `t_dt_pet_class` VALUES (1069, 2, 1, '西藏猎犬');
INSERT INTO `t_dt_pet_class` VALUES (1070, 2, 1, '马士提夫獒犬');
INSERT INTO `t_dt_pet_class` VALUES (1071, 2, 1, '斗牛獒犬');
INSERT INTO `t_dt_pet_class` VALUES (1072, 2, 1, '凯利蓝梗');
INSERT INTO `t_dt_pet_class` VALUES (1073, 2, 1, '法国狼犬');
INSERT INTO `t_dt_pet_class` VALUES (1074, 2, 1, '澳大利亚牧羊犬');
INSERT INTO `t_dt_pet_class` VALUES (1075, 2, 1, '彭布罗克威尔士柯基犬');
INSERT INTO `t_dt_pet_class` VALUES (1076, 2, 1, '英国猎狐犬');
INSERT INTO `t_dt_pet_class` VALUES (1077, 2, 1, '丝毛梗');
INSERT INTO `t_dt_pet_class` VALUES (1078, 2, 1, '匈牙利牧羊犬');
INSERT INTO `t_dt_pet_class` VALUES (1079, 2, 1, '拳狮犬');
INSERT INTO `t_dt_pet_class` VALUES (1080, 2, 1, '山地犬');
INSERT INTO `t_dt_pet_class` VALUES (1081, 2, 1, '罗得西亚脊背犬');
INSERT INTO `t_dt_pet_class` VALUES (1082, 2, 1, '西藏梗');
INSERT INTO `t_dt_pet_class` VALUES (1083, 2, 1, '湖畔梗');
INSERT INTO `t_dt_pet_class` VALUES (1084, 2, 1, '爱尔兰雪达犬');
INSERT INTO `t_dt_pet_class` VALUES (1085, 2, 1, '瑞典柯基犬');
INSERT INTO `t_dt_pet_class` VALUES (1086, 2, 1, '芬兰拉普猎犬');
INSERT INTO `t_dt_pet_class` VALUES (1087, 2, 1, '德国宾莎犬');
INSERT INTO `t_dt_pet_class` VALUES (1088, 2, 1, '库瓦兹犬');
INSERT INTO `t_dt_pet_class` VALUES (1089, 2, 1, '奇努克犬');
INSERT INTO `t_dt_pet_class` VALUES (1090, 2, 1, '巨型雪纳瑞犬');
INSERT INTO `t_dt_pet_class` VALUES (1091, 2, 1, '萨路基猎犬');
INSERT INTO `t_dt_pet_class` VALUES (1092, 2, 1, '维希拉猎犬');
INSERT INTO `t_dt_pet_class` VALUES (1093, 2, 1, '澳大利亚牧牛犬');
INSERT INTO `t_dt_pet_class` VALUES (1094, 2, 1, '威尔士梗');
INSERT INTO `t_dt_pet_class` VALUES (1095, 2, 1, '格雷伊猎犬');
INSERT INTO `t_dt_pet_class` VALUES (1096, 2, 1, '普罗特猎犬');
INSERT INTO `t_dt_pet_class` VALUES (1097, 2, 1, '墨西哥无毛犬');
INSERT INTO `t_dt_pet_class` VALUES (1098, 2, 1, '短毛猎狐梗');
INSERT INTO `t_dt_pet_class` VALUES (1099, 2, 1, '小型斗牛梗');
INSERT INTO `t_dt_pet_class` VALUES (1100, 2, 1, '斯塔福郡斗牛梗');
INSERT INTO `t_dt_pet_class` VALUES (1101, 2, 1, '威玛犬');
INSERT INTO `t_dt_pet_class` VALUES (1102, 2, 1, '意大利灰狗');
INSERT INTO `t_dt_pet_class` VALUES (1103, 2, 1, '荷兰毛狮犬');
INSERT INTO `t_dt_pet_class` VALUES (1104, 2, 1, '爱尔兰水猎犬');
INSERT INTO `t_dt_pet_class` VALUES (1105, 2, 1, '冰岛牧羊犬');
INSERT INTO `t_dt_pet_class` VALUES (1106, 2, 1, '安纳托利亚牧羊犬');
INSERT INTO `t_dt_pet_class` VALUES (1107, 2, 1, '美国猎狐犬');
INSERT INTO `t_dt_pet_class` VALUES (1108, 2, 1, '帕尔森罗塞尔梗');
INSERT INTO `t_dt_pet_class` VALUES (1109, 2, 1, '短脚长身梗');
INSERT INTO `t_dt_pet_class` VALUES (1110, 2, 1, '英国跳猎犬');
INSERT INTO `t_dt_pet_class` VALUES (1111, 2, 1, '爱尔兰梗');
INSERT INTO `t_dt_pet_class` VALUES (1112, 2, 1, '挪威伦德猎犬');
INSERT INTO `t_dt_pet_class` VALUES (1113, 2, 1, '挪威猎鹿犬');
INSERT INTO `t_dt_pet_class` VALUES (1114, 2, 1, '西帕基犬');
INSERT INTO `t_dt_pet_class` VALUES (1115, 2, 1, '波兰低地牧羊犬');
INSERT INTO `t_dt_pet_class` VALUES (1116, 2, 1, '黑俄罗斯梗');
INSERT INTO `t_dt_pet_class` VALUES (1117, 2, 1, '苏格兰猎鹿犬');
INSERT INTO `t_dt_pet_class` VALUES (1118, 2, 1, '挪威梗');
INSERT INTO `t_dt_pet_class` VALUES (1119, 2, 1, '爱尔兰红白雪达犬');
INSERT INTO `t_dt_pet_class` VALUES (1120, 2, 1, '大瑞士山地犬');
INSERT INTO `t_dt_pet_class` VALUES (1121, 2, 1, '罗秦犬');
INSERT INTO `t_dt_pet_class` VALUES (1122, 2, 1, '那不勒斯獒');
INSERT INTO `t_dt_pet_class` VALUES (1123, 2, 1, '捷克梗');
INSERT INTO `t_dt_pet_class` VALUES (1124, 2, 1, '比利时马林诺斯犬');
INSERT INTO `t_dt_pet_class` VALUES (1125, 2, 1, '标准型雪纳瑞犬');
INSERT INTO `t_dt_pet_class` VALUES (1126, 2, 1, '锡利哈姆梗');
INSERT INTO `t_dt_pet_class` VALUES (1127, 2, 1, '德国短毛波音达');
INSERT INTO `t_dt_pet_class` VALUES (1128, 2, 1, '红骨猎浣熊犬');
INSERT INTO `t_dt_pet_class` VALUES (1129, 2, 1, '巴仙吉犬');
INSERT INTO `t_dt_pet_class` VALUES (1130, 2, 1, '戈登雪达犬');
INSERT INTO `t_dt_pet_class` VALUES (1131, 2, 1, '诺福克梗');
INSERT INTO `t_dt_pet_class` VALUES (1132, 2, 1, '小型葡萄牙波登可犬');
INSERT INTO `t_dt_pet_class` VALUES (1133, 2, 1, '骑士查理王小猎犬');
INSERT INTO `t_dt_pet_class` VALUES (1134, 2, 1, '美国斯塔福郡梗');
INSERT INTO `t_dt_pet_class` VALUES (1135, 2, 1, '切萨皮克海湾寻回犬');
INSERT INTO `t_dt_pet_class` VALUES (1136, 2, 1, '粗毛柯利犬');
INSERT INTO `t_dt_pet_class` VALUES (1137, 2, 1, '玩具曼彻斯特犬');
INSERT INTO `t_dt_pet_class` VALUES (1138, 2, 1, '比利时特伏丹犬');
INSERT INTO `t_dt_pet_class` VALUES (1139, 2, 1, '玩具猎狐梗');
INSERT INTO `t_dt_pet_class` VALUES (1140, 2, 1, '日本忡');
INSERT INTO `t_dt_pet_class` VALUES (1141, 2, 1, '爱尔兰峡谷梗');
INSERT INTO `t_dt_pet_class` VALUES (1142, 2, 1, '澳大利亚梗');
INSERT INTO `t_dt_pet_class` VALUES (1143, 2, 1, '芬兰波美拉尼亚丝毛狗');
INSERT INTO `t_dt_pet_class` VALUES (1144, 2, 1, '猎水獭犬');
INSERT INTO `t_dt_pet_class` VALUES (1145, 2, 1, '挪威布哈德犬');
INSERT INTO `t_dt_pet_class` VALUES (1146, 2, 1, '爱尔兰软毛梗');
INSERT INTO `t_dt_pet_class` VALUES (1147, 2, 1, '卷毛寻回犬');
INSERT INTO `t_dt_pet_class` VALUES (1148, 2, 1, '弗莱特寻回犬');
INSERT INTO `t_dt_pet_class` VALUES (1149, 2, 1, '英国玩具犬');
INSERT INTO `t_dt_pet_class` VALUES (1150, 2, 1, '迦南犬');
INSERT INTO `t_dt_pet_class` VALUES (1151, 2, 1, '猴头梗');
INSERT INTO `t_dt_pet_class` VALUES (1152, 2, 1, '布鲁塞尔格里芬犬');
INSERT INTO `t_dt_pet_class` VALUES (1153, 2, 1, '德国硬毛波音达');
INSERT INTO `t_dt_pet_class` VALUES (1154, 2, 1, '布雷猎犬');
INSERT INTO `t_dt_pet_class` VALUES (1155, 2, 1, '黑褐猎浣熊犬');
INSERT INTO `t_dt_pet_class` VALUES (1156, 2, 1, '布列塔尼犬');
INSERT INTO `t_dt_pet_class` VALUES (1157, 2, 1, '美国水猎犬');
INSERT INTO `t_dt_pet_class` VALUES (1158, 2, 1, '西班牙小猎犬');
INSERT INTO `t_dt_pet_class` VALUES (1159, 2, 1, '树丛浣熊猎犬');
INSERT INTO `t_dt_pet_class` VALUES (1160, 2, 1, '波兰德斯布比野犬');
INSERT INTO `t_dt_pet_class` VALUES (1161, 2, 1, '比利牛斯牧羊犬');
INSERT INTO `t_dt_pet_class` VALUES (1162, 2, 1, '史毕诺犬');
INSERT INTO `t_dt_pet_class` VALUES (1163, 2, 1, '伊比赞猎犬');
INSERT INTO `t_dt_pet_class` VALUES (1164, 2, 1, '凯斯梗');
INSERT INTO `t_dt_pet_class` VALUES (1165, 2, 1, '美国英国猎浣熊犬');
INSERT INTO `t_dt_pet_class` VALUES (1166, 2, 1, '布鲁克浣熊猎犬');
INSERT INTO `t_dt_pet_class` VALUES (1167, 2, 1, '迷你贝吉格里芬凡丁犬');
INSERT INTO `t_dt_pet_class` VALUES (1168, 2, 1, '新斯科舍猎鸭寻猎犬');
INSERT INTO `t_dt_pet_class` VALUES (1169, 2, 1, '捕鼠梗');
INSERT INTO `t_dt_pet_class` VALUES (1170, 2, 1, '英格兰雪达犬');
INSERT INTO `t_dt_pet_class` VALUES (1171, 2, 1, '田野小猎犬');
INSERT INTO `t_dt_pet_class` VALUES (1172, 2, 1, '威尔士跳猎犬');
INSERT INTO `t_dt_pet_class` VALUES (1173, 2, 1, '博得猎狐犬');
INSERT INTO `t_dt_pet_class` VALUES (1174, 2, 1, '苏塞克斯猎犬');
INSERT INTO `t_dt_pet_class` VALUES (1175, 2, 1, '硬毛指示格里芬犬');
INSERT INTO `t_dt_pet_class` VALUES (1176, 2, 1, '博伊金猎犬');