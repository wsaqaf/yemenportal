class PostViewRegistrar
  def initialize(post:, user:, user_ip:)
    @post = post
    @user = user
    @user_ip = user_ip
  end

  def commit_view
    if authorized_user_first_view? || unauthorized_user_first_view?
      commit_post_view
    end
  end

  private

  attr_reader :post, :user, :user_ip

  def authorized_user_first_view?
    user.present? && there_is_no_view_for_user?
  end

  def unauthorized_user_first_view?
    user.blank? && there_is_no_view_for_ip?
  end

  def there_is_no_view_for_user?
    !PostView.exists?(post: post, user: user)
  end

  def there_is_no_view_for_ip?
    !PostView.exists?(post: post, ip_hash: ip_hash)
  end

  def commit_post_view
    PostView.create(post: post, user: user, ip_hash: ip_hash)
  end

  def ip_hash
    @_ip_hash ||= Digest::MD5.hexdigest(user_ip)
  end
end
