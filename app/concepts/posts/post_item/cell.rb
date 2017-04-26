class Posts::PostItem::Cell < Application::Cell
  PREVIEW_SIZE = 180

  property :title, :link, :published_at, :description, :id, :category_ids, :categories, :source

  private

  def category_names
    categories.map(&:name)
  end

  def post_info
    time = l published_at, format: :created_at
    "#{time} #{source.name}"
  end
end
