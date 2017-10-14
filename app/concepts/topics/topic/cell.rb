class Topics::Topic::Cell < Application::Cell
  private

  def topic
    model
  end

  def upvoted_class_if_upvoted
    "js-upvoted" if topic.upvoted_by_user?
  end

  def downvoted_class_if_downvoted
    "js-downvoted" if topic.downvoted_by_user?
  end

  def description
    truncate(topic.description, length: 300, separator: " ")
  end

  def link_to_more
    if title.blank?
      link_to(st("details"), path_to_topic)
    end
  end

  def path_to_topic
    if topic.show_internally?
      #post_url(initial_post, protocol: "http")
      post_url(initial_post, protocol: "http", host: "yp.local", port: 3001, root: root_url)
    else
      topic.link
    end
  end

  def initial_post
    topic.initial_post
  end

  def title
    topic.title
  end
end
