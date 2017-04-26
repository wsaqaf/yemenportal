class Posts::PostItem::Cell < Application::Cell
  PREVIEW_SIZE = 180

  property :title, :link, :published_at, :description, :id, :category_ids, :categories, :source

  private

  def category_names
    categories.map(&:name)
  end
end
