class Sources::Item::Cell < Application::Cell
  def show
    render
  end

  property :link, :id
end
