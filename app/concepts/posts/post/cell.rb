class Posts::Post::Cell < Application::Cell
  private

  property :title, :source_name, :image_url, :voting_result, :description,
    :upvoted_by_user?, :downvoted_by_user?, :category_names, :published_at,
    :show_internally?, :link, :main_post_of_topic?, :related_posts, :topic_id,
    :main_topic, :related_post_of_topic?

  option :related_posts_count, :hide_link_to_related, :truncate_description

  def post
    model
  end

  def upvoted_class_if_upvoted
    "js-upvoted" if upvoted_by_user?
  end

  def downvoted_class_if_downvoted
    "js-downvoted" if downvoted_by_user?
  end

  def post_description
    if truncate_description
      truncate(description, length: 250, separator: " ")
    else
      description
    end
  end

  def post_category_names
    category_names.join(", ")
  end

  def link_to_more
    if title.blank?
      link_to(st("details"), path_to_post)
    end
  end

  def path_to_post
    if show_internally?
      post_url(post, protocol: "http")
    else
      link
    end
  end

  def post_related_posts
    if related_posts_count.present?
      related_posts.first(related_posts_count)
    else
      related_posts
    end
  end

  def path_to_topic
    @_path_to_topic ||= load_path_to_topic
  end

  def load_path_to_topic
    if main_post_of_topic?
      topic_path(main_topic)
    elsif related_post_of_topic?
      topic_path(topic_id)
    end
  end

  def topic_link_title
    @_topic_link_title ||= load_topic_link_title
  end

  def load_topic_link_title
    if related_post_of_topic? || main_post_with_few_related?
      st("show_topic")
    elsif main_post_with_many_related?
      st("show_more_related")
    end
  end

  def main_post_with_few_related?
    related_posts.any? && !related_posts_count_more_than_showing?
  end

  def main_post_with_many_related?
    related_posts.any? && related_posts_count_more_than_showing?
  end

  def related_posts_count_more_than_showing?
    related_posts.count > related_posts_count
  end

  def show_link_to_related?
    !hide_link_to_related && topic_link_title.present? && path_to_topic.present?
  end

  delegate :image_url, to: :post, prefix: true, allow_nil: true
end
