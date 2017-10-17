class Posts::Reviews::Comment::Cell < Application::Cell
  private

  def comment
    model
  end

  def post
    options[:post]
  end

  def deletable_by_current_user?
    policy(comment).destroy?
  end
end
