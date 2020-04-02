import argg_hdl as ah
import argg_hdl.examples as ahe 


tb = ahe.InputDelay_tb()
ah.convert_to_hdl(tb, "pyhdl_waveform")