# Pet API doc

## pagination
使用DRF [LimitOffsetPagination](https://www.django-rest-framework.org/api-guide/pagination/#limitoffsetpagination)，
默认分页大小10

## error handling
- 正常请求返回200系列code
- 请求错误返回非200系列code
  - 401表示需要登录
  - 403表示当前权限不允许查看当前内容
  - 404表示请求的对象不存在或url错误
  - 500表示出现服务端bug，需要修复
  - 可能包含的错误信息包括`detail`字段
  - 或post数据验证失败时会返回`[{'field': 'messg'}, ...]`, `field`为错误字段名，`msg`为错误内容

## 时间
默认时间格式化方式为iso-8601
 - `*_time` 为datetime字符串 ，e.g. 北京时间`2019-02-17T15:50:00+08:00`
 - `*_date` 为date字符串，e.g. `2019-02-17`


## 枚举 status & type
  ```
FLAG_CHOICE = (
    (0, '否'),
    (1, '是'),
)
GENDER_CHOICE = (
    (0, u'未知'),
    (1, u'男'),
    (2, u'女'),
)
CASE_STATUS = (
    (0, u'有效'),
    (1, u'已关闭'),
    (2, u'已过期'),
)
AUDIT_STATUS = (
    (0, '待审核'),
    (1, '已通过'),
    (2, '已拒绝'),
)
CHARGE_STATUS = (
    (0, '未付款'),
    (1, '付款失败'),
    (2, '付款成功'),
    (3, '免费'),
)
CONTACT_STATUS = (
    (0, 'NotContact'),
    (1, 'Contacted'),
)
BOOST_KPI_TYPE = (
    (0, '无'),
    (1, '浏览量'),
)
MEDICAL_STATUS = (
	(0, '无'),
	(1, '已绝育'),
	(2, '已免疫'),
	(3, '已除虫'),
)
PET_TYPE = (
    (0, '其他'),
    (1, '猫'),
    (2, '狗'),
)
FOUND_STATUS = (
    (0, '不在身边'),
    (1, '在身边'),
    (2, '在医院'),
)
MATERIAL_TYPE = (
    (0, '视频'),
    (1, '图片'),
)
MESSAGE_TYPE = (
    (0, '系统'),
    (1, '私信'),
)
READ_STATUS = (
    (0, '未读'),
    (1, '已读'),
)
BANNER_TYPE = (
    (0, '默认'),
    (1, '广告'),
    (2, '寻宠'),
    (3, '寻主'),
)
  ```


## lost
Lost对象字段 `('id', 'publisher', 'nickname', 'species', 'pet_type', 'gender', 'lost_time', 'place',
                  'color', 'description', 'material_set', 'tags', 'medical_status', 'reward', 'birthday',
                  'longitude', 'latitude', 'view_count', 'repost_count', 'like_count',
                  'case_status', 'audit_status', 'publish_charge_status')`
`pet_type` 猫/狗/其他
`species` 品种
`medical_status` `,`逗号分隔字符串


1. `/pet/losts/` 
  - `GET` 返回lost列表，时间倒序排列，接受参数
    - `pet_type` 
    - `longitude`， 坐标小数，搜索范围0.1, 约22KM正方形范围
    - `latitude` 和`longitude`同时使用
    - `date_range` 发布天数，和地点取交集
  - `POST` 新建lost对象, tags字段可以直接使用自定义字符串列表，会自动创建新tag或复用已存在tag
    - `publisher` 所有与当前用户有关的字段如publisher, sender, 不允许上传，使用请求验证的用户
    - `material_set` 为素材id，先通过material 接口上传素材，获取id后再创建对象

2. `/pet/lost/<id>` 
  - `GET` 返回lost对象
  - `POST` 修改对象，成功返回对象数据
  - `DELETE` 删除对象，标记为无效数据
3. `/pet/lost/match/<id>`
  - `GET` 返回匹配`lost<id>`的Found对象列表，可能是距离/时间/类型关联上的found，也包括直接提交的founda
  - `POST` 创建匹配`lost<id>`的Found对象，成功返回对象数据
4. `/pet/lost/case/<id>`
  - `GET` 修改lost状态，参数`case_status`, 0-有效，1-已结案，2-已关闭，返回对象

## found
Found 对象字段 `('id', 'publisher', 'species', 'pet_type', 'color','gender',
                 'tags', 'place', 'found_time' 'description', 'latitude', 'longitude',
                 'found_status', 'case_status', 'audit_status', 'liked',
                 'view_count', 'like_count', 'repost_count', 'material_set')`
1. `/pet/founds` 同 `/pet/losts`
2. `/pet/found/<id>` 同 `/pet/lost/<id>`
3. `/pet/found/match/<id>` 同 `/pet/lost/match/<id>`
4. `/pet/found/case/<id>` 同 `/pet/lost/case/<id>`


## material 
Material对象字段`('id', 'url', 'thumb_url')`

1. `/pet/material/upload`
  - `PUT` 创建material，图片内容填充进http请求`FILE`部分，`Content-Type`为mime-type，目前仅支持图片，jpg/png均可，不要用gif，成功返回material对象
2. `/pet/material/<id>`
  - `GET` 返回对象
  - `DELETE` 删除对象


## species
Species对象字段 `('id', 'pet_type', 'name')`，`pet_type`: 1-猫, 2-狗, 0-其他
1. `/pet/species`
   - `GET` 返回对象列表， 接受参数`pet_type`，返回`top: [species*9], ordered: [species...]`，top按照引用数量排序，ordered按照拼音首字母排序

## actions
action: 点赞like, 转发repost, 收藏follow
obj: lost, found

1. `/pet/action/<action>/<obj>/<id>/`
  - `GET` 记录点赞/转发/收藏，参数`cancel=1`取消，返回action成功后的数量统计`{'count': <int>}`


## comment
Comment评论字段 `('id', 'publisher', 'reply_to', 'create_time',  'content',
                  'last_update_time')`

1. `/pet/comment/<obj>/<id>`
  - `GET` 返回object(found/lost)相关的评论，时间正序排列
  - `POST` 新建评论，成功返回对象

## message & message thread
Message消息/私信，字段`('id', 'content', 'read_status', 'create_time', receiver', 'sender', 'lost', 'found')`, 其中`lost/found`对应消息关联的发布信息

MessageThread 消息对话，用户a和用户b之间的对话，字段`('id', 'sender', 'receiver', 'read', 'new', 'last_msg', 'msg_type')`, `messages`对应`Message`数组, 
`read` 已读消息的最大id，`new` 未读消息数量，一个会话会分别为消息双方用户分别创建不同的msgthread

1. `/pet/msg/threads/` 对话列表
  - `GET` 返回对话列表，未分页 
  - `POST` 新建对话，返回对象数据

2. `/pet/msg/thread/<id>` 消息列表
  - `GET` 返回消息列表，未分页，返回 MessageAndThread `{"thread": {....}, "msgs": [{....}]}`
  - `POST` 新建消息，返回对象数据

3. `/pet/msg/thread` 新建或获得消息会话
  - `GET` 参数 receiver=<user_id> 为当前用户和receiver创建新会话或返回已存在会话内容，返回会话对象
<del>
4. `/pet/msg/thread/<obj>/<id>`
  - `GET` 关联obj到thread（点击obj的私信按钮，记录该行为），返回MessageAndThread
  </del>


## user follow
用户关注列表，数据混合lost/found, 字段 `('id', 'lost', 'found')`

1. `/pet/user/follow`
  - `GET` 返回分页列表，obj创建时间倒序

## user posts
用户发布列表

1. `/pet/user/lost` 
  - `GET` 返回分页列表
2. `/pet/user/found`
  - `GET` 返回分页列表


## tag
字段 `('count', 'name')`

1. `/pet/tag`
  - `GET` 返回tag列表，包含`top_tag`和 `user_tag` 2个列表， 2者可能存在重复
  - `POST` 新建tag

## banner
字段 `('id', 'img', 'start_time', 'end_time', 'banner_type', 'click_url')`，`banner_type`:0-默认，1-广告，2-寻宠，3-寻主
1. `/pet/banners`
  - `GET` 返回有效banner列表，参数`num`指定banner数量，默认5, 参数`type`指定banner类型，会追加0,1两种类型
2. `/pet/banner/<pk>` pk为id，banner点击跳转，返回302
