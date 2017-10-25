class Posts::Reviews::Cell < Application::Cell
  private

  property :post, :flags, :comments, :new_review_comment

  def can_current_user_create_comment?
    policy(ReviewComment).create?
  end

  def can_current_user_update_post?
    policy(Post).update?
  end

  def all_categories
    Category.all
  end

  def selected_category_ids
    post.category_ids
  end
end
