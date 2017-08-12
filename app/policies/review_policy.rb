class ReviewPolicy < ApplicationPolicy
  def create?
    moderator? || admin?
  end
end
