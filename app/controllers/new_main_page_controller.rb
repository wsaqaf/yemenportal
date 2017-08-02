class NewMainPageController < ApplicationController
  def show
    render cell: true, model: Topic.ordered_by_date.paginate(page: params[:page])
  end
end
