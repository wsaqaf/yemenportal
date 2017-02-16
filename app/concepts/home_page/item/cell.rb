class HomePage::Item::Cell < Rails::View
  def show
    render
  end

  private

  property :title, :link, :pub_date, :description

end
