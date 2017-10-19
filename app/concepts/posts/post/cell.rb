class Posts::Post::Cell < Application::Cell
  private

  property :title, :source_name, :image_url, :voting_result, :description,
    :upvoted_by_user?, :downvoted_by_user?, :category_names, :created_at,
    :show_internally?, :link, :main_post_of_topic?, :related_posts

  option :related_posts_count

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
    truncate(description, length: 300, separator: " ")
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

  def topic_link_title
    if main_post_of_topic? && !related_posts.empty?
      st("show_more_related")
    else
      st("show_topic")
    end
  end

  delegate :image_url, to: :post, prefix: true, allow_nil: true
end
