class HomePage::Item::Cell < Rails::View
  def show
    render
  end

  property :title, :link, :pub_date, :description
end
