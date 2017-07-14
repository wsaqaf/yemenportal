class Posts::Show::Cell < Application::Cell
  option :comments, :user_id
  property :title, :link, :published_at, :description, :id, :category_ids, :categories, :source, :photo_url, :state

  def field_name(field)
    t("post.fields.#{field}")
  end

  def category_names
    categories.map(&:name)
  end

  def path
    posts_path(state: "pending")
  end

  def render_comments
    concept("posts/comments/cell", collection: comments.to_a, user_id: user_id, destroy_path: nil)
  end

  def read_post_link
    source.iframe_flag ? post_reader_path(post_id: id) : link
  end
end
