class Posts::HeadersController < ApplicationController
  def show
    allow_header_frame_render
    render cell: :show, model: post, layout: "post_header_layout"
  end

  private

  def post
    ::Post.include_voted_by_user(current_user).find(params[:post_id])
  end

  def allow_header_frame_render
    response.headers["X-Frame-Options"] = "ALLOWALL"
  end
end
