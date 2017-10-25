class PostPolicy < ApplicationPolicy
  def update?
    moderator? || admin?
  end
end
