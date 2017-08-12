class ReviewPolicy < ApplicationPolicy
  def create?
    moderator? || admin?
  end

  def destroy?
    (review.moderator == current_user) && (moderator? || admin?)
  end

  private

  def review
    record
  end
end
