class Posts::CategoriesController < ApplicationController
  before_action :authenticate_user!

  def update
    authorize ::Post
    render json: { category_names: updated_categories_names }
  end

  private

  def updated_categories_names
    categories_updater.updated_category_names
  end

  def categories_updater
    @_categories_updater ||= Posts::CategoriesUpdater.new(params)
  end
end
