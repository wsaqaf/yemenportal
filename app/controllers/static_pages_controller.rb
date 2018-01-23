class StaticPagesController < ApplicationController
  def terms_of_use
    render cell: "static_pages/terms_of_use"
  end

  def about_us
    render cell: "static_pages/about_us"
  end

  def qs_and_as
    render cell: "static_pages/qs_and_as"
  end

end
