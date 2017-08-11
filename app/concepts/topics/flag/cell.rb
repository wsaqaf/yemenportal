class Topics::Flag::Cell < Application::Cell
  private

  def flag
    model
  end

  def reviewed_by_user_class
    if flag.topic_reviewed_by_user?
      "topic-flag--flagged"
    else
      "topic-flag--unflagged"
    end
  end
end
