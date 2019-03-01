from django.core.exceptions import PermissionDenied
from django.http import Http404
from pet.models import *

def init_user_system_threads(user):
    for i in range(1, 4):
        msg_thr, _ = MessageThread.objects.get_or_create(user=user, msg_type=i)
        # TODO(zlz): create welcome message for user


def get_or_create_thread_by_user(user_a, user_b):
    if user_a.id > user_b.id:
        user_a, user_b = user_b, user_a
    elif user_a.id == user_b.id:
        raise PermissionDenied
    msg_thread = MessageThread.objects.filter(user_a=user_a, user_b=user_b).first()
    if msg_thread is None:
        msg_thread = MessageThread(user_a=user_a, user_b=user_b)
        msg_thread.save()
    return msg_thread


def create_system_msg(msg, user_list):
    pass

def update_msg_thread(msg):
    if msg.msg_type == 0:
        update_private_msg_thread(msg)
    elif msg.msg_type == 1:
        update_publisher_msg_thread(msg)
    elif msg.msg_type == 3:
        update_system_msg_thread(msg)

def update_system_msg_thread(msg):
    msg_threads = MessageThread.objects.filter(msg_type=3)
    msg_threads.update(new=F('new')+1, hide=False)

def update_private_msg_thread(msg):
    sender, receiver = msg.sender, msg.receiver
    msg_type = msg.msg_type
    sender_thread, create = MessageThread.objects.get_or_create(user=sender,
                                                                peer=receiver,
                                                                msg_type=msg_type)
    sender_thread.messages.add(msg)
    receiver_thread, create = MessageThread.objects.get_or_create(peer=sender,
                                                                  user=receiver,
                                                                  msg_type=msg_type)
    receiver_thread.messages.add(msg)
    new_msgs = receiver_thread.messages.filter(id__gt=receiver_thread.read)
    new_count = new_msgs.count()
    if new_count > 0 and receiver_thread.new != new_count:
        receiver_thread.new = new_count
        receiver_thread.hide = False
    receiver_thread.save()
    sender_thread.save()
    if receiver_thread.hide:
        return None
    else:
        return receiver_thread


def update_publisher_msg_thread(msg):
    if msg.lost is not None:
        user = msg.lost.publisher
    elif msg.found is not None:
        user = msg.found.publisher

    msg_thread = MessageThread.objects.filter(user=user, peer=None, msg_type=1).first()
    if msg_thread is None:
        init_user_system_threads(user)
        msg_thread = MessageThread.objects.filter(user=user, peer=None, msg_type=1).first()
    msg_thread.messages.add(msg)
    msg_thread.hide = False
    msg_thread.new += 1
    msg_thread.save()


def create_new_comment_msg(instance, inst_type):
    msg_template = u'您发布的%s启事有新的留言'

    msg = Message(receiver=instance.publisher, msg_type=1)
    if inst_type == 'lost':
        msg.content = msg_template % u'寻宠'
        msg.lost = instance
    elif inst_type == 'found':
        msg.content = msg_template % u'寻主'
        msg.found = instance
    else:
        raise RuntimeError
    msg.save()





