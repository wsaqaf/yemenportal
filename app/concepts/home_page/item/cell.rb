class HomePage::Item::Cell < Application::Cell
  def show
    render
  end

  property :title, :link, :pub_date, :description
end
