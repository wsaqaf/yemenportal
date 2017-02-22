class Categories::Cell < Application::Cell
  def show
    render
  end

  private

  property :name

  def table_body
    concept("categories/item/cell", collection: model.to_a)
  end
end
