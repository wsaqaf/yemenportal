class NewMainPage::Cell < Application::Cell
  private

  def topics
    model
  end

  def upvoted_class_if_upvoted(topic)
    "js-upvoted" if topic.upvoted_by_user?
  end

  def downvoted_class_if_downvoted(topic)
    "js-downvoted" if topic.downvoted_by_user?
  end
end
