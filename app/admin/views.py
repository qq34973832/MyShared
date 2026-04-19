from sqladmin import ModelView

from app.models import (
    APIToken,
    AdCampaign,
    AdEvent,
    Bid,
    Category,
    ChatMessage,
    Comment,
    ConsumerProfile,
    Merchant,
    SharedProduct,
    Subscription,
    User,
    UserPermission,
    Webhook,
    WebhookLog,
)


class BaseAdminView(ModelView):
    can_view_details = True
    page_size = 50
    page_size_options = [25, 50, 100]


class UserAdmin(BaseAdminView, model=User):
    name = "用户"
    name_plural = "用户"
    icon = "fa-solid fa-users"
    can_create = False
    column_list = [
        User.id,
        User.username,
        User.email,
        User.role,
        User.is_active,
        User.is_banned,
        User.created_at,
    ]
    column_searchable_list = [User.username, User.email]
    column_sortable_list = [User.id, User.username, User.email, User.role, User.created_at]
    column_filters = [User.role, User.is_active, User.is_banned]
    form_columns = [User.username, User.email, User.role, User.is_active, User.is_banned, User.ban_reason, User.permissions, User.metadata_]


class UserPermissionAdmin(BaseAdminView, model=UserPermission):
    name = "用户权限"
    name_plural = "用户权限"
    icon = "fa-solid fa-key"
    column_list = [UserPermission.id, UserPermission.user_id, UserPermission.permission, UserPermission.created_at]
    column_searchable_list = [UserPermission.permission]


class MerchantAdmin(BaseAdminView, model=Merchant):
    name = "商家"
    name_plural = "商家"
    icon = "fa-solid fa-store"
    column_list = [Merchant.id, Merchant.shop_name, Merchant.user_id, Merchant.is_verified, Merchant.total_products, Merchant.rating]
    column_searchable_list = [Merchant.shop_name, Merchant.contact_email, Merchant.contact_phone]
    column_filters = [Merchant.is_verified]


class ConsumerProfileAdmin(BaseAdminView, model=ConsumerProfile):
    name = "消费者档案"
    name_plural = "消费者档案"
    icon = "fa-solid fa-user"
    column_list = [ConsumerProfile.id, ConsumerProfile.user_id, ConsumerProfile.nickname, ConsumerProfile.created_at]
    column_searchable_list = [ConsumerProfile.nickname]


class CategoryAdmin(BaseAdminView, model=Category):
    name = "商品分类"
    name_plural = "商品分类"
    icon = "fa-solid fa-sitemap"
    column_list = [Category.id, Category.name, Category.slug, Category.merchant_id, Category.parent_id, Category.sort_order]
    column_searchable_list = [Category.name, Category.slug]


class SharedProductAdmin(BaseAdminView, model=SharedProduct):
    name = "商品"
    name_plural = "商品"
    icon = "fa-solid fa-box"
    column_list = [SharedProduct.id, SharedProduct.name, SharedProduct.merchant_id, SharedProduct.category_id, SharedProduct.current_price, SharedProduct.stock, SharedProduct.is_available]
    column_searchable_list = [SharedProduct.name, SharedProduct.sku]
    column_filters = [SharedProduct.is_available]


class BidAdmin(BaseAdminView, model=Bid):
    name = "竞价"
    name_plural = "竞价"
    icon = "fa-solid fa-gavel"
    column_list = [Bid.id, Bid.product_id, Bid.merchant_id, Bid.bid_price, Bid.status, Bid.bid_amount]
    column_searchable_list = [Bid.status]
    column_filters = [Bid.status]


class AdCampaignAdmin(BaseAdminView, model=AdCampaign):
    name = "广告活动"
    name_plural = "广告活动"
    icon = "fa-solid fa-bullhorn"
    column_list = [AdCampaign.id, AdCampaign.name, AdCampaign.merchant_id, AdCampaign.status, AdCampaign.daily_budget, AdCampaign.total_budget, AdCampaign.is_active]
    column_searchable_list = [AdCampaign.name]
    column_filters = [AdCampaign.status, AdCampaign.is_active]


class AdEventAdmin(BaseAdminView, model=AdEvent):
    name = "广告事件"
    name_plural = "广告事件"
    icon = "fa-solid fa-chart-line"
    can_create = False
    column_list = [AdEvent.id, AdEvent.campaign_id, AdEvent.event_type, AdEvent.event_count, AdEvent.cost, AdEvent.event_time]
    column_searchable_list = [AdEvent.event_type, AdEvent.anonymous_id]
    column_filters = [AdEvent.event_type]


class CommentAdmin(BaseAdminView, model=Comment):
    name = "评论"
    name_plural = "评论"
    icon = "fa-solid fa-comments"
    column_list = [Comment.id, Comment.user_id, Comment.product_id, Comment.rating, Comment.title, Comment.helpful_count, Comment.created_at]
    column_searchable_list = [Comment.title, Comment.content]
    column_filters = [Comment.rating]


class ChatMessageAdmin(BaseAdminView, model=ChatMessage):
    name = "聊天消息"
    name_plural = "聊天消息"
    icon = "fa-solid fa-message"
    column_list = [ChatMessage.id, ChatMessage.user_id, ChatMessage.merchant_id, ChatMessage.message_type, ChatMessage.is_read, ChatMessage.created_at]
    column_searchable_list = [ChatMessage.content, ChatMessage.context]
    column_filters = [ChatMessage.message_type, ChatMessage.is_read]


class SubscriptionAdmin(BaseAdminView, model=Subscription):
    name = "订阅"
    name_plural = "订阅"
    icon = "fa-solid fa-bell"
    column_list = [Subscription.id, Subscription.consumer_id, Subscription.merchant_id, Subscription.category_id, Subscription.product_id, Subscription.subscription_type, Subscription.is_active]
    column_searchable_list = [Subscription.subscription_type]
    column_filters = [Subscription.subscription_type, Subscription.is_active]


class APITokenAdmin(BaseAdminView, model=APIToken):
    name = "开放接口令牌"
    name_plural = "开放接口令牌"
    icon = "fa-solid fa-plug"
    column_list = [APIToken.id, APIToken.user_id, APIToken.name, APIToken.is_active, APIToken.is_revoked, APIToken.expires_at, APIToken.last_used_at]
    column_searchable_list = [APIToken.name, APIToken.token]
    column_filters = [APIToken.is_active, APIToken.is_revoked]


class WebhookAdmin(BaseAdminView, model=Webhook):
    name = "Webhook"
    name_plural = "Webhook"
    icon = "fa-solid fa-link"
    column_list = [Webhook.id, Webhook.name, Webhook.url, Webhook.is_active, Webhook.created_at]
    column_searchable_list = [Webhook.name, Webhook.url]
    column_filters = [Webhook.is_active]


class WebhookLogAdmin(BaseAdminView, model=WebhookLog):
    name = "Webhook 日志"
    name_plural = "Webhook 日志"
    icon = "fa-solid fa-file-lines"
    can_create = False
    column_list = [WebhookLog.id, WebhookLog.webhook_id, WebhookLog.event, WebhookLog.status_code, WebhookLog.retry_count, WebhookLog.is_success, WebhookLog.created_at]
    column_searchable_list = [WebhookLog.event, WebhookLog.error_message]
    column_filters = [WebhookLog.is_success, WebhookLog.status_code]


ADMIN_VIEWS = [
    UserAdmin,
    UserPermissionAdmin,
    MerchantAdmin,
    ConsumerProfileAdmin,
    CategoryAdmin,
    SharedProductAdmin,
    BidAdmin,
    AdCampaignAdmin,
    AdEventAdmin,
    CommentAdmin,
    ChatMessageAdmin,
    SubscriptionAdmin,
    APITokenAdmin,
    WebhookAdmin,
    WebhookLogAdmin,
]
