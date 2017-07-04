class PostTagPolicy < ApplicationPolicy
  attr_reader :post, :user

  def initialize(user, post)
    @user = user
    @post = post
  end

  def new?
    raise Pundit::NotAuthorizedError, "Post was resolved" if PostTag.resolve(user, post).present?
  end
end
