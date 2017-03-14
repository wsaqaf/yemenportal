class Posts::Pending::Item::Cell < Application::Cell
  def show
    render
  end

  property :title, :link, :published_at, :description, :id
end
