package FrisbeeSim;
import java.awt.EventQueue;

import javax.swing.JFrame;
import java.awt.BorderLayout;
import javax.swing.SpringLayout;
import javax.swing.JPanel;
import javax.swing.JTextField;
import javax.swing.JLabel;
import javax.swing.JButton;
import java.awt.event.KeyAdapter;
import java.awt.event.KeyEvent;
import java.awt.event.ActionListener;
import java.awt.event.ActionEvent;
import java.math.*;
import java.util.Iterator;
import java.util.List;
import org.jfree.data.xy.XYDataset;
import org.jfree.data.xy.XYDataItem;
//graphing util
import org.jfree.data.xy.XYSeries;
import org.jfree.data.xy.XYSeriesCollection;
import org.jfree.chart.JFreeChart;
import org.jfree.chart.ChartFactory;
import org.jfree.chart.plot.PlotOrientation;
import org.jfree.chart.ChartPanel;
import org.jfree.chart.ChartFrame;
import javax.swing.border.SoftBevelBorder;
import javax.swing.border.BevelBorder;
import org.jfree.chart.plot.XYPlot;
import javax.swing.SwingConstants;
import java.awt.event.FocusAdapter;
import java.awt.event.FocusEvent;
import java.awt.Component;
import javax.swing.Box;
import java.awt.event.MouseAdapter;
import java.awt.event.MouseEvent;
import net.miginfocom.swing.MigLayout;
import java.awt.Dimension;

public class FrisbeeUI {

	// Constants on the robot in SI units
	private final static double HEIGHT = 1;//m
	private final static double SPEED = 14;//m/s
	private final static double DELTA_T = .001;
	private final static double TOLERANCE = .2; //+ or - m
	private final static double METER_CONVERSION = .3048;
	private final static double MAX_ANGLE = 50;
	
	private JFrame frmFrisbeeSim;
	private JTextField txtDistance;
	private JTextField txtHeight;
	private JLabel lblXDistance;
	private JLabel lblHeight;
	private ChartPanel pnlGraph;
	private JTextField txtAngle;
	private JLabel lblAngleToShoo;
	private JTextField txtSpeed;
	private JLabel lblSpeedfts;

	/**
	 * Launch the application.
	 */
	public static void main(String[] args) {
		EventQueue.invokeLater(new Runnable() {
			public void run() {
				try {
					FrisbeeUI window = new FrisbeeUI();
					window.frmFrisbeeSim.setVisible(true);
				} catch (Exception e) {
					e.printStackTrace();
				}
			}
		});
	}

	/**
	 * Create the application.
	 */
	public FrisbeeUI() {
		initialize();
	}

	/*
	 * Returns the heigh and distance for simulation
	 * @param	 None
	 * @return	 X,Y we want to hit
	 */
	public double[] GetHeightAndDistance()
	{
		double x = Double.parseDouble(txtDistance.getText());
		double y = Double.parseDouble(txtHeight.getText());
		double speed = Double.parseDouble(txtSpeed.getText());
		//convert to meters
		x *= METER_CONVERSION;
		y *= METER_CONVERSION;
		speed *= METER_CONVERSION;
		double returnDouble[] = {x, y, speed};
		return returnDouble;
	}
	
	private void Plot(XYSeriesCollection dataSet)
	{
		pnlGraph.setChart(ChartFactory.createXYLineChart(
						"Frisbee Trajectory", // Title
						"Distance", // x-axis Label
						"Height", // y-axis Label
						dataSet, // Dataset
						PlotOrientation.VERTICAL, // Plot Orientation
						true, // Show Legend
						true, // Use tooltips
						false// Configure chart to generate URLs?
						));
	}
	
	private void FindPlotAngle()
	{
		double[] target = GetHeightAndDistance();
		XYSeriesCollection dataSet = new XYSeriesCollection();
		boolean possible = false;
		for( double angle = 0; angle < MAX_ANGLE; angle += .1 )
		{
			//speed is constant but angle determines speed of X and Y
			double speedX = target[2] * Math.cos(Math.toRadians(angle));
			double speedY = target[2] * Math.sin(Math.toRadians(angle));
			//calculate the trajectory
			XYSeries xyCord = Frisbee.simulate(HEIGHT, speedX, speedY, angle, DELTA_T);
			//if the max doesn't reach the goal no use in trying to find
			// where the goal hits, abort!
			if (xyCord.getMaxX() < target[0] || xyCord.getMaxY() < target[1])
			{
				possible = false;
				continue;
			}
			List<XYDataItem> cordList = xyCord.getItems();
			Iterator<XYDataItem> iterator = cordList.iterator();
			while(iterator.hasNext())
			{
				XYDataItem point = iterator.next();
				double x = point.getXValue();
				double y = point.getYValue();
				//if the distance is with in tolerance we are good
				double diffX = x - target[0]/METER_CONVERSION;
				double diffY = y - target[1]/METER_CONVERSION;
				double diff = Math.sqrt(Math.pow(diffX, 2) + Math.pow(diffY, 2));
				if(diff < TOLERANCE)
				{
					possible = true;
					txtAngle.setText(String.format("%.2f", angle));
					dataSet.addSeries(xyCord);
					Plot(dataSet);
					break;	
				}

			}
			
			if( possible == true)
			{
				break;
			}
			
		}
		if( possible == false)
			txtAngle.setText("Impossible");
	}
	/**
	 * Initialize the contents of the frame.
	 */
	private void initialize() {
		frmFrisbeeSim = new JFrame();
		frmFrisbeeSim.setSize(new Dimension(800, 450));
		frmFrisbeeSim.setTitle("Frisbee Sim");
		XYPlot plot =  new	XYPlot();
		JFreeChart chart = new JFreeChart(plot);
		SpringLayout springLayout = new SpringLayout();
		frmFrisbeeSim.getContentPane().setLayout(springLayout);
		pnlGraph = new ChartPanel(chart);
		springLayout.putConstraint(SpringLayout.WEST, pnlGraph, 7, SpringLayout.WEST, frmFrisbeeSim.getContentPane());
		springLayout.putConstraint(SpringLayout.SOUTH, pnlGraph, 344, SpringLayout.NORTH, frmFrisbeeSim.getContentPane());
		springLayout.putConstraint(SpringLayout.EAST, pnlGraph, 748, SpringLayout.WEST, frmFrisbeeSim.getContentPane());
		pnlGraph.setBorder(new SoftBevelBorder(BevelBorder.LOWERED, null, null, null, null));
		frmFrisbeeSim.getContentPane().add(pnlGraph);
		
		txtDistance = new JTextField();
		springLayout.putConstraint(SpringLayout.NORTH, pnlGraph, 6, SpringLayout.SOUTH, txtDistance);
		springLayout.putConstraint(SpringLayout.NORTH, txtDistance, 31, SpringLayout.NORTH, frmFrisbeeSim.getContentPane());
		springLayout.putConstraint(SpringLayout.WEST, txtDistance, 36, SpringLayout.WEST, frmFrisbeeSim.getContentPane());
		txtDistance.addMouseListener(new MouseAdapter() {
			@Override
			public void mouseClicked(MouseEvent e) {
				if (txtDistance.getText() == "")
					txtDistance.setText("0.0");
			}
		});
		txtDistance.setHorizontalAlignment(SwingConstants.CENTER);
		txtDistance.setText("0.0");
		txtDistance.addKeyListener(new KeyAdapter() {
			@Override
			public void keyTyped(KeyEvent e) {
				char key =  e.getKeyChar();
				if(key == '.' && txtDistance.getText().contains("."))
					e.consume();
				if (!Character.isDigit(key) && key != '.' && key != 8 )
					e.consume();
			}
		});
		frmFrisbeeSim.getContentPane().add(txtDistance);
		txtDistance.setColumns(10);
		
		txtHeight = new JTextField();
		springLayout.putConstraint(SpringLayout.EAST, txtHeight, -53, SpringLayout.EAST, frmFrisbeeSim.getContentPane());
		txtHeight.setHorizontalAlignment(SwingConstants.CENTER);
		txtHeight.setText("0.0");
		txtHeight.addKeyListener(new KeyAdapter() {
			@Override
			public void keyTyped(KeyEvent e) {
				char key =  e.getKeyChar();
				if(key == '.' && txtHeight.getText().contains("."))
					e.consume();
				if (!Character.isDigit(key) && key != '.' && key != 8 )
					e.consume();
			}
		});
		txtHeight.setColumns(10);
		frmFrisbeeSim.getContentPane().add(txtHeight);
		
		lblXDistance = new JLabel("X Distance(ft)");
		springLayout.putConstraint(SpringLayout.NORTH, lblXDistance, 11, SpringLayout.NORTH, frmFrisbeeSim.getContentPane());
		springLayout.putConstraint(SpringLayout.WEST, lblXDistance, 47, SpringLayout.WEST, frmFrisbeeSim.getContentPane());
		frmFrisbeeSim.getContentPane().add(lblXDistance);
		
		lblHeight = new JLabel("Height(ft)");
		springLayout.putConstraint(SpringLayout.NORTH, txtHeight, 6, SpringLayout.SOUTH, lblHeight);
		springLayout.putConstraint(SpringLayout.SOUTH, txtHeight, 26, SpringLayout.SOUTH, lblHeight);
		springLayout.putConstraint(SpringLayout.NORTH, lblHeight, 0, SpringLayout.NORTH, lblXDistance);
		springLayout.putConstraint(SpringLayout.EAST, lblHeight, -91, SpringLayout.EAST, frmFrisbeeSim.getContentPane());
		frmFrisbeeSim.getContentPane().add(lblHeight);
		
		Component glue = Box.createGlue();
		pnlGraph.add(glue);
		
		Component glue_1 = Box.createGlue();
		springLayout.putConstraint(SpringLayout.NORTH, glue_1, 7, SpringLayout.NORTH, frmFrisbeeSim.getContentPane());
		springLayout.putConstraint(SpringLayout.WEST, glue_1, 7, SpringLayout.WEST, frmFrisbeeSim.getContentPane());
		frmFrisbeeSim.getContentPane().add(glue_1);
		
		JButton btnPlot = new JButton("Plot");
		springLayout.putConstraint(SpringLayout.NORTH, btnPlot, 373, SpringLayout.NORTH, frmFrisbeeSim.getContentPane());
		springLayout.putConstraint(SpringLayout.WEST, btnPlot, 364, SpringLayout.WEST, frmFrisbeeSim.getContentPane());
		btnPlot.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent arg0) {
				FindPlotAngle();
			};
		});
		frmFrisbeeSim.getContentPane().add(btnPlot);
		
		txtAngle = new JTextField();
		springLayout.putConstraint(SpringLayout.NORTH, txtAngle, 33, SpringLayout.SOUTH, pnlGraph);
		springLayout.putConstraint(SpringLayout.WEST, txtAngle, 101, SpringLayout.EAST, btnPlot);
		txtAngle.setHorizontalAlignment(SwingConstants.CENTER);
		txtAngle.setEditable(false);
		txtAngle.setText("0.0");
		frmFrisbeeSim.getContentPane().add(txtAngle);
		txtAngle.setColumns(10);
		
		lblAngleToShoo = new JLabel("Shooting Angle (deg)");
		springLayout.putConstraint(SpringLayout.WEST, lblAngleToShoo, 516, SpringLayout.WEST, frmFrisbeeSim.getContentPane());
		springLayout.putConstraint(SpringLayout.SOUTH, lblAngleToShoo, -6, SpringLayout.NORTH, txtAngle);
		springLayout.putConstraint(SpringLayout.EAST, lblAngleToShoo, -130, SpringLayout.EAST, frmFrisbeeSim.getContentPane());
		frmFrisbeeSim.getContentPane().add(lblAngleToShoo);
		
		txtSpeed = new JTextField();
		springLayout.putConstraint(SpringLayout.WEST, txtSpeed, 207, SpringLayout.EAST, txtDistance);
		springLayout.putConstraint(SpringLayout.SOUTH, txtSpeed, -6, SpringLayout.NORTH, pnlGraph);
		txtSpeed.setText(String.format( "%.2f", SPEED / METER_CONVERSION));
		txtSpeed.setHorizontalAlignment(SwingConstants.CENTER);
		txtSpeed.setColumns(10);
		frmFrisbeeSim.getContentPane().add(txtSpeed);
		
		lblSpeedfts = new JLabel("speed(ft/s)");
		springLayout.putConstraint(SpringLayout.NORTH, lblSpeedfts, 0, SpringLayout.NORTH, lblXDistance);
		springLayout.putConstraint(SpringLayout.WEST, lblSpeedfts, 0, SpringLayout.WEST, txtSpeed);
		frmFrisbeeSim.getContentPane().add(lblSpeedfts);
		
	}
}
