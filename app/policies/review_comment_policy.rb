class ReviewCommentPolicy < ApplicationPolicy
  def create?
    moderator? || admin?
  end

  def destroy?
    (moderator? && author?) || admin?
  end

  private

  def review_comment
    record
  end

  def author?
    review_comment.author == current_user
  end
end
