class Posts::PostItem::Cell < Application::Cell
  PREVIEW_SIZE = 180

  option :user
  property :title, :link, :published_at, :description, :id, :category_ids, :categories, :source, :photo_url,
    :same_posts, :post_tags

  private

  def moderator?
    user && (user.role.moderator? || user.role.admin?)
  end

  def category_names
    categories.map(&:name)
  end

  def user_tags
    post_tags.select { |post| post.user == user }.map(&:name)
  end

  def tags_counter
    tags = moderator? ? post_tags.select { |post| post.user != user }.map(&:name) : post_tags.map(&:name)

    Hash[tags.uniq.map { |tag| [tag, tags.count(tag)] }]
  end

  def tag_list
    (Tag.all.map(&:name) + user_tags).uniq
  end

  def read_post_link
    source.iframe_flag ? post_reader_path(post_id: model.id) : link
  end
end
