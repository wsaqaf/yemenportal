class Posts::PostItem::Cell < Application::Cell
  PREVIEW_SIZE = 180

  option :user
  property :title, :link, :published_at, :description, :id, :category_ids, :categories, :source, :photo_url, :post_tags

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
end
