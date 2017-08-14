class Topics::Reviews::Comment::Cell < Application::Cell
  private

  def comment
    model
  end

  def topic
    options[:topic]
  end

  def deletable_by_current_user?
    policy(comment).destroy?
  end
end
