class Topics::Flag::Reviewed::Cell < Topics::Flag::Cell
  private

  def reviewed_by_user_class
    "topic-flag--flagged"
  end

  def button
    button_to(topic_review_path(topic, flag.review), button_options) do
      yield
    end
  end

  def button_options
    super.merge({ method: :delete })
  end
end
