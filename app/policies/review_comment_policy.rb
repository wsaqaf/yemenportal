class ReviewCommentPolicy < ApplicationPolicy
  def create?
    moderator? || admin?
  end

  def destroy?
    (moderator? || admin?) && (review_comment.author == current_user)
  end

  private

  def review_comment
    record
  end
end
