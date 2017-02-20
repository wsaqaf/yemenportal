class Categories::Item::Cell < Application::Cell
  def show
    render
  end

  property :name, :id
end
