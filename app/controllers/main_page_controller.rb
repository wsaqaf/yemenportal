class MainPageController < ApplicationController
  def show
    render cell: true, model: topics_with_voted_attribues
  end

  private

  def topics_with_voted_attribues
    if current_user.present?
      topics.include_voted_by_user(current_user)
    else
      topics
    end
  end

  def topics
    Topic.ordered_by_date.paginate(page: params[:page])
      .includes(posts: [:source, :categories])
  end
end
