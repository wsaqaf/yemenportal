class HomePage::Cell < Application::Cell
  include WillPaginate::ActionView

  def url_for(options)
    parent_controller.url_for(options)
  end

  def show
    render
  end

  private

  option :categories
  property :title, :link, :pub_date, :property

  def table_body
    concept("home_page/item/cell", collection: model.to_a)
  end
end
