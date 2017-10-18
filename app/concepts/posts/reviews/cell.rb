class Posts::Reviews::Cell < Application::Cell
  private

  property :post, :flags, :comments, :new_review_comment

  def can_current_user_create_comment?
    policy(ReviewComment).create?
  end
end
