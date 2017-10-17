class Posts::Post::Cell < Application::Cell
  private

  def post
    model
  end

  # Votes for posts will be implemented later
  def post_voting_result
    0
  end

  def post_description
    truncate(post.description, length: 300, separator: " ")
  end

  def post_category_names
    post.category_names.join(", ")
  end

  def post_created_at
    post.created_at.iso8601
  end

  def link_to_more
    if post_title.blank?
      link_to(st("details"), path_to_post)
    end
  end

  def path_to_post
    if post.show_internally?
      post_url(post, protocol: "http")
    else
      post.link
    end
  end

  delegate :title, :source_name, :source_name, :image_url,
    to: :post, prefix: true, allow_nil: true
end
