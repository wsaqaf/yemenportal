class Posts::PostItem::Cell < Application::Cell
  PREVIEW_SIZE = 180

  property :title, :link, :published_at, :description, :id, :category_ids, :categories

  private

  def category_names
    categories.map(&:name)
  end

  def preview
    ActionView::Base.full_sanitizer.sanitize(description)[0..PREVIEW_SIZE].tr("\n", " ") + "..."
  end
end
