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

  def read_post_link
    source.iframe_flag ? post_reader_path(post_id: model.id) : link
  end

  def tags_counter
    tags = post_tags.map(&:name).reject { |name| name == PostTag::RESOLVE_TAG }

    Hash[tags.uniq.map { |tag| [tag, tags.count(tag)] }]
  end

  def resolve_tag_counter
    post_tags.map(&:name).count(PostTag::RESOLVE_TAG)
  end
end
