class Posts::Comments::Cell < Application::Cell
  option :user_id
  property :user, :body, :created_at, :post

  private

  def delete_path
    post_comment_path(post, model)
  end

  def can_destroy?
    user_id == user.id
  end
end
