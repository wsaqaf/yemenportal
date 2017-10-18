class Posts::Reviews::Comment::Cell < Application::Cell
  private

  property :author, :created_at, :body
  option :post

  def comment
    model
  end

  def deletable_by_current_user?
    policy(comment).destroy?
  end
end
