class Posts::PostItem::Cell < Application::Cell
  PREVIEW_SIZE = 180

  property :title, :link, :published_at, :description, :id, :category_ids, :categories, :source, :photo_url

  private

  def category_names
    categories.map(&:name)
  end

  def read_post_link
    source.iframe_flag ? post_reader_path(post_id: model.id) : link
  end
end
