class CategoriesController < ApplicationController
  def index
    @categories = Category.all
    render cell: true, model: @categories
  end

  def create
    category = Category.new(category_params)

    if category.valid?
      category.save
      redirect_to categories_path
    else
      render cell: "categories/form", model: category
    end
  end

  def new
    category = Category.new
    render cell: :form, model: category
  end

  def destroy
    Category.destroy(params[:id])
    redirect_to categories_path
  end

  private

  def category_params
    params.require(:category).permit(:name)
  end
end
